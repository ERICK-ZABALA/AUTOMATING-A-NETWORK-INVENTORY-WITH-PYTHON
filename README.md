
# AUTOMATING A NETWORK INVENTORY WITH PYTHON

+ how can we talk to the devices?
+ what tool / language will we use?
+ How do we create the list of devices to work with?
+ How will we share our code for others to use?
+ How do we protect any “secrets” (username/password)

# CLI METHOD

* Library to interact: Netmiko, Nornir, NAPALM, Scrapli, PyATS, Ansible, others
* Parse: str.find, regex, TextFSM, pyATS, others
* Spreadsheet: STD CSV

# CREATE VENV PYTHON 3.10.2 WITH PyATS

Note: PyATS just available in environments over Linux.

```bash
[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ python3.10 -m venv inventory

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ cd inventory

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ source inventory/bin/activate

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ python --version
Python 3.10.2
```
In this environment the version of python is `Python 3.10.2` 
```python
(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip list

Package    Version
---------- -------
pip        21.2.4
setuptools 58.1.0
WARNING: You are using pip version 21.2.4; however, version 23.0.1 is available.
You should consider upgrading via the '/home/opc/DEVNET/00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON/inventory/bin/python3.10 -m pip install --upgrade pip' command.

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip install --upgrade pip

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip install pyats[full]


(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip freeze > requirements.txt
```

# DOWNLOAD GUIDE MAKE INVENTORY FROM - HANK PRESTON

* Download in your machine [Summer 2021 Devasc-Prep-Network-Inventory-01](https://github.com/hpreston/summer2021-devasc-prep-network-inventory-01.git) maked by Hank Preston


# CREATE SPREADSHEET

* We are going to create owner `Spreedsheet` [Sample Test Bed File](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file)

PyATS work over YAML consider this point. PyATS uses a testbed.yaml to make an inventory.
We are going to create owner list of devices using this [template](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/_downloads/b05328b78497f390ee873500df1aaa94/SampleTestbedFile.xlsx).

In this template we are going to collect all the devices.

![image](https://user-images.githubusercontent.com/38144008/222002305-9587f85a-bf1e-4aa4-835c-0a2c9d3384d1.png)

We are oing to [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology
). You need an account of cisco to register this sandbox is [free!!!](https://id.cisco.com/signin/register).

![image](https://user-images.githubusercontent.com/38144008/222004497-c3c37576-83cb-4067-927b-ad4704e62d0d.png)

![image](https://user-images.githubusercontent.com/38144008/222009619-eea78d14-3f55-4d08-86e4-5b2a424a3a3c.png)


We are going to register all the devices Cisco in owner file like this:

![image](https://user-images.githubusercontent.com/38144008/222009578-254b6427-95a1-451f-b516-d8b379188bf6.png)

`Username` is requeried to work with the tool and put in blank the section password to `%ASK{}`.

```bash
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  README.md  sample
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ pyats create testbed file --path sample/nso_sandbox_devices.xlsx --output nso_sandbox_testbed.yaml -v
Testbed file generated: 
sample/nso_sandbox_devices.xlsx -> nso_sandbox_testbed.yaml
```
You should see the next file nso_sandbox_testbed.yaml in your virtual environment.

```yaml
devices:
  core-rtr01:
    connections:
      cli:
        ip: 10.10.20.173
        protocol: telnet
    credentials:
      default:
        password: '%ASK{}'
        username: cisco
      enable:
        password: '%ASK{}'
    os: iosxr
    platform: core-rtr01
    type: iosxr ...
```

# IMPROVING US TESTBED FILE

In this section we are going to improve our code alocated the credentials to begin. In this scenario we are working with the same credentials for all devices.

```yaml
testbed:
  credentials:
    default:
      password: '%ASK{}'
      username: '%ASK{}'
    enable:
      password: '%ASK{}'
```

Running: nso_sandbox_testbed_same_credentials.yaml

```bash
inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  nso_sandbox_testbed.yaml  README.md  sample
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ pyats validate testbed --testbed nso_sandbox_testbed_same_credentials.yaml
Loading testbed file: nso_sandbox_testbed_same_credentials.yaml
--------------------------------------------------------------------------------
Enter default password for testbed: cisco

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: cisco

Testbed Name:
    nso_sandbox_testbed_same_credentials

Testbed Devices:
.
|-- core-rtr01 [iosxr/core-rtr01]
|-- core-rtr02 [iosxr/core-rtr02]
|-- dist-rtr01 [iosxe/dist-rtr01]
|-- dist-rtr02 [iosxe/dist-rtr02]
|-- dist-sw01 [nxos/dist-sw01]
|-- dist-sw02 [nxos/dist-sw02]
|-- edge-firewall01 [asa/edge-firewall01]
|-- edge-sw01 [ios/edge-sw01]
-- internet-rtr01 [iosxe/internet-rtr01]
`
YAML Lint Messages
------------------
  4:81      warning  line too long (113 > 80 characters)  (line-length)
  5:81      warning  line too long (81 > 80 characters)  (line-length)
  6:81      warning  line too long (86 > 80 characters)  (line-length)

Warning Messages
----------------
 - Device 'core-rtr01' has no interface definitions
 - Device 'core-rtr02' has no interface definitions
 - Device 'dist-rtr01' has no interface definitions
 - Device 'dist-rtr02' has no interface definitions
 - Device 'dist-sw01' has no interface definitions
 - Device 'dist-sw02' has no interface definitions
 - Device 'edge-firewall01' has no interface definitions
 - Device 'edge-sw01' has no interface definitions
 - Device 'internet-rtr01' has no interface definitions
`
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  `nso_sandbox_testbed_same_credentials.yaml`  nso_sandbox_testbed.yaml  README.md  sample
```
# CONFIGURE VPN CLIENT WITH SANDBOX

+ You need to install telnet in your linux: sudo dnf install telnet

```bash
[opc@jenkins-master ~]$ sudo dnf install telnet
 Package                 Architecture            Version                           Repository                      Size
========================================================================================================================
Installing:
 telnet                  x86_64                  1:0.17-76.el8                     ol8_appstream                   72 k
Transaction Summary
==================================================================================================================

Install  1 Package
Total download size: 72 k
Installed size: 119 k
Is this ok [y/N]: y
Downloading Packages:
telnet-0.17-76.el8.x86_64.rpm                                                           885 kB/s |  72 kB     00:00
------------------------------------------------------------------------------------------------------------------------
Total                                                                                   833 kB/s |  72 kB     00:00
Running transaction check
Transaction check succeeded.
Running transaction test
Transaction test succeeded.
Running transaction
  Preparing        :                                                                                                1/1
  Installing       : telnet-1:0.17-76.el8.x86_64                                                                    1/1
  Running scriptlet: telnet-1:0.17-76.el8.x86_64                                                                    1/1
  Verifying        : telnet-1:0.17-76.el8.x86_64                                                                    1/1

Installed:
  telnet-1:0.17-76.el8.x86_64

Complete!
[opc@jenkins-master ~]$ telnet 8.8.8.8 53
Trying 8.8.8.8...
Connected to 8.8.8.8.
Escape character is '^]'.
```

# Install Sandbox AnyConnect

The Cisco AnyConnect Secure Mobility Client provides users with a secure, private connection to the DevNet Sandbox Labs. 
You will need to install the AnyConnect Client on your system prior to accessing most Sandbox Labs.

[Sandbox AnyConnect](https://pubhub.devnetcloud.com/media/sandbox/site/files/anyconnect-win-4.9.04043-predeploy-k9.zip)

`NOTE: To register your PC in sandbox you need to activate the vpn client; localy`

```bash
[opc@jenkins-master bin]$ mkdir ciscovpn
[opc@jenkins-master bin]$ cd ciscovpn
[opc@jenkins-master bin]$ tar zxf anyconnect-linux64-4.10.05095-predeploy-k9.tar.gz
[opc@jenkins-master bin]$ cd anyconnect-linux64-4.10.05095/
[opc@jenkins-master bin]$ cd vpn/
[opc@jenkins-master bin]$ sudo ./vpn_install.sh
[opc@jenkins-master bin]$ cd /opt/cisco/anyconnect/bin/
[opc@jenkins-master bin]$ sudo ./vpn -s connect devnetsandbox-usw1-reservation.cisco.com:20229

username: cisco
password: cisco

[opc@jenkins-master bin]$ ifconfig

`cscotun0: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1287
        inet 192.168.254.11  netmask 255.255.255.0  destination 192.168.254.11
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 500  (UNSPEC)
        RX packets 2  bytes 138 (138.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2  bytes 138 (138.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
`
ens3: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9000
        inet 10.0.0.25  netmask 255.255.255.0  broadcast 10.0.0.255
        ether 02:00:17:00:10:ef  txqueuelen 1000  (Ethernet)
        RX packets 7461  bytes 1286537 (1.2 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 7055  bytes 2535736 (2.4 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

```

# REFERNCES

+ Creation from Excel File
https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file

+ SANDBOX to test owner Inventory
https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology
