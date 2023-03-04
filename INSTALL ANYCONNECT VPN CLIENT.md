# INSTALL VPN CLIENT ANYCONNECT

To install python in your development environment. You can follow these steps.

+ Download VPN Client Anyconnect via console.

The Cisco AnyConnect Secure Mobility Client provides users with a secure, private connection to the DevNet Sandbox Labs. 
You will need to install the AnyConnect Client on your system prior to accessing most Sandbox Labs.

[Sandbox AnyConnect](https://pubhub.devnetcloud.com/media/sandbox/site/files/anyconnect-win-4.9.04043-predeploy-k9.zip)

`NOTE: To register your PC in sandbox you need to activate the vpn client; localy`

```bash
[opc@jenkins-master bin]$ mkdir ciscovpn
[opc@jenkins-master bin]$ cd ciscovpn

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

# DevNet SANDBOX CISCO

+ In order to have this credentials to connect your environment with Cisco Sandbox, you need to create an account in Cisco and reserve your sandbox Lab.

We are going to go to plataform [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology
). That is time to create an account of cisco to make a login in sandbox it is [free!!!](https://id.cisco.com/signin/register).

![image](https://user-images.githubusercontent.com/38144008/222004497-c3c37576-83cb-4067-927b-ad4704e62d0d.png)

![image](https://user-images.githubusercontent.com/38144008/222009619-eea78d14-3f55-4d08-86e4-5b2a424a3a3c.png)

![image](https://user-images.githubusercontent.com/38144008/222930335-ec242a99-c97d-4c11-9178-350c34193a4d.png)

# TESTING VPN CLIENT WITH DEVNET SANDBOX

```bash
[opc@jenkins-master bin]$ cd /opt/cisco/anyconnect/bin/
[opc@jenkins-master bin]$ sudo ./vpn -s connect devnetsandbox-usw1-reseration.cisco.com:2XXX9

username: cisco.dev
password: XC1sco="

[opc@jenkins-master bin]$ ifconfig

`cscotun0: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1287
        inet 192.168.254.11  netmask 255.255.255.0  destination 192.168.254.11
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 500  (UNSPEC)
        RX packets 2  bytes 138 (138.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2  bytes 138 (138.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
`
ens3: flags=4213<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9000
        inet 10.0.0.25  netmask 255.255.255.0  broadcast 10.0.0.255
        ether 01:00:12:00:10:XX  txqueuelen 1000  (Ethernet)
        RX packets 7461  bytes 1286537 (1.2 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 7055  bytes 2535736 (2.4 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
