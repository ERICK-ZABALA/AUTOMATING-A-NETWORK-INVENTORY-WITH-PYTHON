# INSTALL VPN CLIENT ANYCONNECT

To install python in your development environment. You can follow these steps.

+ Download VPN Client Anyconnect via console.

The Cisco AnyConnect Secure Mobility Client provides users with a secure, private connection to the DevNet Sandbox Labs. 
You will need to install the AnyConnect Client on your system prior to accessing most Sandbox Labs.

[Sandbox AnyConnect](https://pubhub.devnetcloud.com/media/sandbox/site/files/anyconnect-win-4.9.04043-predeploy-k9.zip)


```bash
[opc@jenkins-master bin]$ wget http://www.hostwaydcs.com/CISCO/AnyConnect/anyconnect-linux64-4.10.05095-predeploy-k9.tar.gz
[opc@jenkins-master bin]$ tar zxf anyconnect-linux64-4.10.05095-predeploy-k9.tar.gz

[opc@jenkins-master bin]$ cd anyconnect-linux64-4.10.05095/vpn
[opc@jenkins-master bin]$ sudo ./vpn_install.sh

Installing Cisco AnyConnect Secure Mobility Client...
Supplemental End User License Agreement for AnyConnect(R) Secure Mobility Client v4.x and other VPN-related Software

[licence agreement omitted for brevity]
Please refer to the Cisco Systems, Inc. End User License Agreement.
http://www.cisco.com/en/US/docs/general/warranty/English/EU1KEN_.html

Do you accept the terms in the license agreement? [y/n] y
You have accepted the license agreement.
Please wait while Cisco AnyConnect Secure Mobility Client is being installed...
Starting Cisco AnyConnect Secure Mobility Client Agent...
Done!

[opc@jenkins-master bin]$ cd /opt/cisco/anyconnect/bin/
[opc@jenkins-master bin]$ sudo ./vpn -s connect devnetsandbox-usw1-reservation.cisco.com:20229

Username: cisco.dev
Password: XC1sco=
```

# CREATE AN EXECUTABLE FILE - VPN CLIENT

Open a text editor and enter the following commands:

```bash
[opc@jenkins-master ]$ # sudo nano vpnconnect.sh
```
Copy this code in the file vpnconnect.sh

```bash
!/bin/bash
cd /opt/cisco/anyconnect/bin/
./vpn -s connect devnetsandbox-usw1-reservation.cisco.com:20229 <<EOF
cisco.dev
XC1sco="
EOF
```
Save the file with a descriptive name, such as "vpn_connect.sh".

Open a terminal and navigate to the location where you saved the file.

Run the following command to make the file executable:

`[opc@jenkins-master ]$ chmod +x vpn_connect.sh`

`[opc@jenkins-master ]$./vpn_connect.sh`

# DevNet Sandbox Cisco

+ In order to have this credentials to connect your environment with Cisco Sandbox, you need to create an account in Cisco and reserve your sandbox Lab.

We are going to go to plataform [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology
). That is time to create an account of cisco to make a login in sandbox it is [free!!!](https://id.cisco.com/signin/register).

![image](https://user-images.githubusercontent.com/38144008/222004497-c3c37576-83cb-4067-927b-ad4704e62d0d.png)

![image](https://user-images.githubusercontent.com/38144008/222009619-eea78d14-3f55-4d08-86e4-5b2a424a3a3c.png)

![image](https://user-images.githubusercontent.com/38144008/222930335-ec242a99-c97d-4c11-9178-350c34193a4d.png)
