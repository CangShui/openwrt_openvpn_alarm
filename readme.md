监控OpenWrt OpenVPN登录事件，**实时发送Telegram通知**！

## 功能特性
- ✅ **登录成功**：用户名 + IP + 时间 + 平台 + 客户端版本
- ❌ **密码错误**：IP + 时间
- 📱 **Telegram推送**


## 安装python
```
opkg update && opkg install python3 python3-pip
```
## 我的Openwrt环境
```
LuCI openwrt-24.10 branch 26.337.67860~daf821a
luci-app-openvpn - 25.337.67860~daf821a - LuCI Support for OpenVPN
luci-app-openvpn-client - 20250227-r5 - LuCI support for OpenVPN Client
luci-app-openvpn-server - 2.0-r14 - LuCI support for OpenVPN Server
luci-app-openvpn-server-client - 6.0-r4 - LuCI support for OpenVPN Server
```

##注册服务
```
cat > /etc/init.d/openvpn_alarm << 'EOF'
#!/bin/sh /etc/rc.common

START=99
STOP=10
APP="/usr/bin/python3 /root/vpn_alarm.py"
PIDFILE="/var/run/openvpn_alarm.pid"

start() {
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE"); then
        echo "$APP 已在运行"
        return 0
    fi
    
    echo "启动 OpenVPN 监控..."
    nohup $APP > /dev/null 2>&1 &
    echo $! > $PIDFILE
    echo "PID: $(cat $PIDFILE)"
}

stop() {
    if [ -f "$PIDFILE" ]; then
        kill $(cat $PIDFILE)
        rm -f $PIDFILE
        echo "已停止 OpenVPN 监控"
    fi
}

restart() {
    stop
    sleep 2
    start
}
EOF
```
```
chmod +x /etc/init.d/openvpn_alarm
/etc/init.d/openvpn_alarm enable
/etc/init.d/openvpn_alarm start

```






## 服务命令
```
# 启动
/etc/init.d/openvpn_alarm start

# 停止
/etc/init.d/openvpn_alarm stop

# 重启
/etc/init.d/openvpn_alarm restart

# 开机自启状态
/etc/init.d/openvpn_alarm enabled && echo "已启用" || echo "未启用"

# 查看进程
ps | grep vpn_alarm.py
cat /var/run/openvpn_alarm.pid
```


<img width="1707" height="529" alt="image" src="https://github.com/user-attachments/assets/db9d08b8-e0e8-4d43-871c-20ab162764fe" />


<img width="951" height="739" alt="image" src="https://github.com/user-attachments/assets/bc1190b4-7b2d-4a91-8ed4-5d086ee5d953" />
