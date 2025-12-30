#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#我的Openwrt环境
#LuCI openwrt-24.10 branch 26.337.67860~daf821a
#opkg update && opkg install python3 python3-pip
#luci-app-openvpn - 25.337.67860~daf821a - LuCI Support for OpenVPN
#luci-app-openvpn-client - 20250227-r5 - LuCI support for OpenVPN Client
#luci-app-openvpn-server - 2.0-r14 - LuCI support for OpenVPN Server
#luci-app-openvpn-server-client - 6.0-r4 - LuCI support for OpenVPN Server

import time
import re
import os
import requests

# Telegram配置
TELEGRAM_TOKEN = '123456:AAAAAAAAAAA_XXXXXXXXXXXXXX'
TELEGRAM_CHAT_ID = '-1008888888888'
LOG_FILE = '/tmp/openvpn.log'

def send_telegram(msg):
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': msg,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.status_code == 200
    except:
        return False

def monitor_openvpn():
    if not os.path.exists(LOG_FILE):
        print(f"❌ 日志文件 {LOG_FILE} 不存在")
        return
        
    print(f"开始监控 OpenVPN 日志: {LOG_FILE}")
    print(f"Telegram Token: {TELEGRAM_TOKEN[:20]}... 已配置")
    

    with open(LOG_FILE, 'r') as f:
        f.seek(0, 2)  # 移到文件末尾
        initial_pos = f.tell()

    seen_events = set()
    last_pos = initial_pos  # 从末尾开始监控
    recent_lines = []
    is_first_run = True
    
    while True:
        try:
            with open(LOG_FILE, 'r') as f:
                f.seek(last_pos)
                new_lines = f.readlines()
                last_pos = f.tell()
                
                # 首次运行跳过已有日志，只处理真正的新日志
                if is_first_run and new_lines:
                    print("⏭️ 首次运行，下次刷新日志时开始监控")
                    is_first_run = False
                    continue
                
                for line in new_lines:
                    line = line.strip()
                    if line:
                        recent_lines.append(line)
                        if len(recent_lines) > 30:
                            recent_lines.pop(0)
                        
                        # 1. 登录成功
                        auth_success = re.search(r"TLS: Username/Password authentication succeeded for username '(\w+)'", line)
                        if auth_success:
                            username = auth_success.group(1)
                            timestamp = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line).group(1)
                            event_key = f"SUCCESS:{username}:{timestamp}"
                            
                            if event_key not in seen_events:
                                seen_events.add(event_key)
                                
                                client_ip = 'Unknown IP'
                                platform = 'Unknown'
                                version = 'Unknown'
                                
                                for recent_line in recent_lines[-15:]:
                                    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', recent_line)
                                    if ip_match and client_ip == 'Unknown IP':
                                        client_ip = ip_match.group(1)
                                    
                                    plat_match = re.search(r'IV_PLAT=(\w+)', recent_line)
                                    if plat_match and platform == 'Unknown':
                                        platform = plat_match.group(1)
                                    
                                    ver_match = re.search(r'IV_GUI_VER=([^,\s]+)', recent_line)
                                    if ver_match and version == 'Unknown':
                                        version = ver_match.group(1)
                                
                                print(f"✅ 用户「{username}」地址「{client_ip}」登录时间: {timestamp} 📱 平台: {platform} 🆚 版本: {version}")

                                
                                tg_msg = f"""<b>🚀 OpenVPN登录成功</b>
👤 用户: <code>{username}</code>
🌐 地址: <code>{client_ip}</code>
🕐 时间: {timestamp}
🆚 版本: {version}
                                """
                                
                                if send_telegram(tg_msg):
                                    print("📱 Telegram发送成功 ✅")
                                    print("-" * 60)
                                else:
                                    print("📱 Telegram发送失败 ❌")
                                    print("-" * 60)
                        
                        # 2. 密码错误
                        auth_failed = re.search(r"TLS Auth Error: Auth Username/Password verification failed for peer", line)
                        if auth_failed:
                            client_ip = 'Unknown IP'
                            timestamp = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line).group(1)
                            
                            for recent_line in recent_lines[-20:]:
                                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', recent_line)
                                if ip_match:
                                    client_ip = ip_match.group(1)
                                    break
                            
                            event_key = f"FAILED:{client_ip}:{timestamp}"
                            if event_key not in seen_events:
                                seen_events.add(event_key)
                                print(f"❌ 用户 地址「{client_ip}」密码错误！登录时间: {timestamp}")
                                
                                tg_msg = f"""<b>❌ OpenVPN密码错误</b>
🌐 地址: <code>{client_ip}</code>
🕐 时间: {timestamp}
                                """
                                
                                if send_telegram(tg_msg):
                                    print("📱 Telegram发送成功 ✅")
                                    print("-" * 60)
                                else:
                                    print("📱 Telegram发送失败 ❌")
                                    print("-" * 60)
                
                if not new_lines:
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"监控错误: {e}")
            time.sleep(1)

if __name__ == '__main__':
    monitor_openvpn()
