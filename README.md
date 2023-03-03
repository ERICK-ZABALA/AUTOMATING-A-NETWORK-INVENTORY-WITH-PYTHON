
# AUTOMATING A NETWORK INVENTORY WITH PYTHON

+ how can we talk to the devices?
+ what tool / language will we use?
+ How do we create the list of devices to work with?
+ How will we share our code for others to use?
+ How do we protect any “secrets” (username/password)

# METHOD CLI

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

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip install "pyats[full]"


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
# CONFIGURE TELNET IN YOUR LOCAL HOST

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

# INSTALL VPN CLIENT - ANYCONNECT

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
+ Use your credentials to connect via anyconnect.

![image](https://user-images.githubusercontent.com/38144008/222144917-3e1dd19a-9752-4aef-a372-1293a9ccce48.png)

```bash
[opc@jenkins-master bin]$ cd /opt/cisco/anyconnect/bin/
[opc@jenkins-master bin]$ sudo ./vpn -s connect devnetsandbox-usw1-reservation.cisco.com:20229

username: mr.cisco
password: cisco%

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

[opc@jenkins-master profile]$ telnet 10.10.20.172

'Trying 10.10.20.172...
Connected to 10.10.20.172.
Escape character is '^]'.
CC
**************************************************************************
* IOSv is strictly limited to use for evaluation, demonstration and IOS  *
* education. IOSv is provided as-is and is not supported by Cisco''s      *
* Technical Advisory Center. Any use or disclosure, in whole or in part, *
* of the IOSv Software or Documentation to any third party for any       *
* purposes is expressly prohibited except as otherwise authorized by     *
* Cisco in writing.                                                      *
**************************************************************************

User Access Verification

Password: CC
**************************************************************************
* IOSv is strictly limited to use for evaluation, demonstration and IOS  *
* education. IOSv is provided as-is and is not supported by Cisco''s     *
* Technical Advisory Center. Any use or disclosure, in whole or in part, *
* of the IOSv Software or Documentation to any third party for any       *
* purposes is expressly prohibited except as otherwise authorized by     *
* Cisco in writing.                                                      *
**************************************************************************
edge-sw01>en
Password:
edge-sw01#exit
Connection closed by foreign host.
```
# TESTING IF CLI WORK WITH PYATS

+ We are going to validate if working CLI with PyATS 

```bash
inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  nso_sandbox_testbed_same_credentials.yaml  nso_sandbox_testbed.yaml  README.md  sample
```

```bash
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ pyats parse "show version" --testbed nso_sandbox_testbed_same_credentials.yaml
Enter default password for testbed: cisco

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: cisco
  0%|                                                                                                                          | 0/1 [00:00<?, ?it/s

  {
  "chassis_detail": "IOS XRv Chassis",
  "config_register": "0x2102",
  "device_family": "IOS XRv Series",
  "image": "bootflash:disk0/xrvr-os-mbi-6.3.1/mbixrvr-rp.vm",
  "main_mem": "cisco IOS XRv Series (Pentium II Stepping 7) processor with 3145215K bytes of memory.",
  "operating_system": "IOSXR",
  "processor": "Pentium II Stepping 7",
  "processor_memory_bytes": "3145215K",
  "rp_config_register": "0x2102",
  "software_version": "6.3.1",
  "uptime": "7 hours, 30 minutes"
}

100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:06<00:00,  6.22s/it]
  0%|                                                                                                                          | 0/1 [00:00<?, ?it/s]{
  ...
```

![image](https://user-images.githubusercontent.com/38144008/222148411-97c31e44-5128-40de-821c-f85b4dedceec.png)

# CLI APPROACH WORKS WITH PYATS - PARSE

When we are using "pyats parse" in some devices the command "show version" is not available for example in "edge-firewall01 | asa". Not all is perfect :(.

PyATS return: `dicts/Lists or JSON format`

```bash
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ pyats parse "show version" --testbed nso_sandbox_testbed_same_credentials.yaml

Enter default password for testbed: cisco
Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: cisco
  
  0%|                                                                                                                          | 0/1 [00:00<?, ?it/s]{
  "chassis_detail": "IOS XRv Chassis",
  "config_register": "0x2102",
  "device_family": "IOS XRv Series",
  "image": "bootflash:disk0/xrvr-os-mbi-6.3.1/mbixrvr-rp.vm",
  "main_mem": "cisco IOS XRv Series (Pentium II Stepping 7) processor with 3145215K bytes of memory.",
  "operating_system": "IOSXR",
  "processor": "Pentium II Stepping 7",
  "processor_memory_bytes": "3145215K",
  "rp_config_register": "0x2102",
  "software_version": "6.3.1",
  "uptime": "1 day, 10 hours, 14 minutes"
}
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:06<00:00,  6.44s/it]
  0%| 
```

That is the information to generate us report inventory csv file.

```json
"operating_system": "IOSXR",
"software_version": "6.3.1",
"uptime": "1 day, 10 hours, 14 minutes"
```

if you pyats parse not found the specific command "show version" you probably receive this answer.

```bash
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.20it/s]

  0%|                                                                                                                          | 0/1 [00:00<?, ?it/s]Issue with the parser show version


Traceback (most recent call last):
  File "src/genie/cli/commands/parser.py", line 339, in genie.cli.commands.parser.ParserCommand.parse
  File "src/genie/conf/base/device.py", line 531, in genie.conf.base.device.Device.parse
  File "src/genie/conf/base/device.py", line 578, in genie.conf.base.device.Device._get_parser_output
TypeError: device is not connected, output must be provided.
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 414.87it/s]
```
+ How to resolve this problem?

  Well, the solution to this type of problem is Python; Yes we need to create a script using Python.

+ Create a script in python and executable `chmod +x network_inventory.py`.

![image](https://user-images.githubusercontent.com/38144008/222495857-2ce07c78-d329-4326-8933-ac9f19b16f80.png)


```bash
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ chmod +x network_inventory.py
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  'network_inventory.py'  nso_sandbox_testbed_same_credentials.yaml  nso_sandbox_testbed.yaml  README.md  sample
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$
```
# PYTHON SCRIPTING FOR NETWORK CONNECTIVITY TESTING WITH PyATS

This command `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml` permit to verify your concetivity from PyATS, script and network access.

```bash
(inventory)  devnet@Devnet  ~/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON   main ±  `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

Creating a network inventory script.
Namespace(testbed='nso_sandbox_testbed_same_credentials.yaml')
Enter default password for testbed: 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: 
<Testbed object 'nso_sandbox_testbed_same_credentials' at 0x7fa854c41fc0>

2023-03-02 21:43:19,858: %UNICON-INFO: +++ core-rtr02 logfile /tmp/core-rtr02-cli-20230302T214319855.log +++

2023-03-02 21:43:19,861: %UNICON-INFO: +++ Unicon plugin iosxr (unicon.plugins.iosxr) +++
```
# TEST 2 - DISABLE LOGS IN PARSE

+ Disabling logs using parser

```python
#!/home/devnet/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/inventory/bin/python
"""
That is an script basic that permit capture an inventory of our network 
using CLI as "show version" and "show inventory".

Goal:
 - Create a CSV inventory file over this parameters: device name, software version, uptime, serial number
"""

# Start our program from main
from pyats.topology.loader import load


if __name__ == "__main__":
    import argparse

    print("####################################")
    print("Creating a Network Inventory script.")
    print("####################################")

    # Load pyATS testbed
    parser = argparse.ArgumentParser(prog = 'NETWORK INVENTORY',description='General network inventory report')
    parser.add_argument('testbed', type=str, help='pyATS Testbed File')
    args = parser.parse_args()
    print(f"Loading testbed file: {args.testbed}")

    # Create pyATS testbed object
    testbed =load(args.testbed)
    print(f"Connecting to all devices in testbed: {testbed.name}")

    # Connect to network devices
    testbed.connect(log_stdout=False)
    
    # Run command to gather output from devices

    # Disconnect from network devices
    for device in testbed.devices:
        print(f"Disconnecting from device {device}.")
        testbed.devices[device].disconnect()
    
    # Built inventory report over data structure

    # Generate a CSV File of data
    
```
CLI: `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

```bash
(inventory)  devnet@Devnet  ~/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON   main ±  ./network_inventory.py nso_sandbox_testbed_same_credentials.yaml

####################################
Creating a Network Inventory script.
####################################
Loading testbed file: nso_sandbox_testbed_same_credentials.yaml
Enter default password for testbed: 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: 
Connecting to all devices in testbed: nso_sandbox_testbed_same_credentials
```
# CREATING SHOW VERSION & SHOW INVENTORY

```python
#!/home/devnet/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/inventory/bin/python
"""
That is an script basic that permit capture an inventory of our network 
using CLI as "show version" and "show inventory".

Goal:
 - Create a CSV inventory file over this parameters: device name, software version, uptime, serial number
"""

# Start our program from main
from pyats.topology.loader import load


if __name__ == "__main__":
    import argparse

    print("####################################")
    print("Creating a Network Inventory script.")
    print("####################################")

    # Load pyATS testbed
    parser = argparse.ArgumentParser(prog = 'NETWORK INVENTORY',description='General network inventory report')
    parser.add_argument('testbed', type=str, help='pyATS Testbed File')
    args = parser.parse_args()
    print(f"Loading testbed file: {args.testbed}")

    # Create pyATS testbed object
    testbed =load(args.testbed)
    print(f"Connecting to all devices in testbed: {testbed.name}")

    # Connect to network devices
    testbed.connect(log_stdout=False)
    
    # Run command to gather output from devices
    show_version={}
    show_inventory={}

    for device in testbed.devices:
        print(f"Gatherin show version from device {device}")
        show_version[device] = testbed.devices[device].parse("show version")
        print(f"{device} show version: {show_version[device]}")

        print(f"Gatherin show version from device {device}")
        show_inventory[device] = testbed.devices[device].parse("show inventory")
        print(f"{device} show inventory: {show_inventory[device]}")
        
        

    # Disconnect from network devices
    for device in testbed.devices:
        print(f"Disconnecting from device {device}.")
        testbed.devices[device].disconnect()
    
    # Built inventory report over data structure

    # Generate a CSV File of data
  
```

CLI:`./network_inventory.py nso_sandbox_testbed_same_credentials.yaml `

```bash
inventory)  devnet@Devnet  ~/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON   main ±  ./network_inventory.py nso_sandbox_testbed_same_credentials.yaml 
####################################
Creating a Network Inventory script.
####################################
Loading testbed file: nso_sandbox_testbed_same_credentials.yaml
Enter default password for testbed:cisco 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: cisco
Connecting to all devices in testbed: nso_sandbox_testbed_same_credentials
Traceback (most recent call last): 
```

# REFERNCES

+ Creation from Excel File
https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file

+ SANDBOX to test owner Inventory
https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology
