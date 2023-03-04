# INSTALL VPN CLIENT ANYCONNECT

To install python in your development environment. You can follow these steps.

+ Download VPN Client Anyconnect via console.

```bash
[opc@jenkins-master bin]$ wget http://www.hostwaydcs.com/CISCO/AnyConnect/anyconnect-linux64-4.10.05095-predeploy-k9.tar.gz

[opc@jenkins-master bin]$ tar zxf anyconnect-linux64-4.10.05095-predeploy-k9.tar.gz

[opc@jenkins-master bin]$ cd anyconnect-linux64-4.10.05095/vpn

[opc@jenkins-master bin]$ sudo ./vpn_install.sh

[opc@jenkins-master bin]$ cd /opt/cisco/anyconnect/bin/
[opc@jenkins-master bin]$ sudo ./vpn -s connect devnetsandbox-usw1-reservation.cisco.com:20229

Username: cisco.dev
Password: XC1sco=
```

# CREATE AN EXECUTABLE FILE - VPN CLIENT


+ In order to have this credentials to connect your environment with Cisco Sandbox, you need to create an account in Cisco and reserve your sandbox Lab.

We are going to go to plataform [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology
). That is time to create an account of cisco to make a login in sandbox it is [free!!!](https://id.cisco.com/signin/register).

![image](https://user-images.githubusercontent.com/38144008/222004497-c3c37576-83cb-4067-927b-ad4704e62d0d.png)

![image](https://user-images.githubusercontent.com/38144008/222009619-eea78d14-3f55-4d08-86e4-5b2a424a3a3c.png)

