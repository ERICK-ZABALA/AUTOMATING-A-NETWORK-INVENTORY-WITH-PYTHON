
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

Sometimes parsers can not be included in some plataforms, that is the reason of this error.(in asa device).

## error parse asa device:

![image](https://user-images.githubusercontent.com/38144008/222657835-750906d3-ce8a-486e-9a2c-f030455aefad.png)




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
Note: Verify your `shebang` in your script.

![image](https://user-images.githubusercontent.com/38144008/222668149-ef8217cf-c85a-478a-894d-8ca389d0c0e2.png)

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
(inventory)  devnet@Devnet  ~/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON   main ±  ./network_inventory_02.py nso_sandbox_testbed_same_credentials.yaml
####################################
Creating a Network Inventory script.
####################################
Loading testbed file: nso_sandbox_testbed_same_credentials.yaml
Enter default password for testbed: 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: 
Connecting to all devices in testbed: nso_sandbox_testbed_same_credentials
Disconnecting from device core-rtr01.
Disconnecting from device core-rtr02.
Disconnecting from device dist-rtr01.
Disconnecting from device dist-rtr02.
Disconnecting from device dist-sw01.
Disconnecting from device dist-sw02.
Disconnecting from device edge-firewall01.
Disconnecting from device edge-sw01.
Disconnecting from device internet-rtr01.
```
![image](https://user-images.githubusercontent.com/38144008/222666104-5c4f2a7a-3ee8-4f4f-b810-82631a7a8c64.png)

# GATHERING SHOW VERSION & SHOW INVENTORY

In this section we are going to display show version and show inventory from python script.

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
        print(f"\nGatherin show version from device {device}")
        show_version[device] = testbed.devices[device].parse("show version")
        print(f"{device} show version: {show_version[device]}")

        print(f"Gatherin show inventory from device {device}")
        show_inventory[device] = testbed.devices[device].parse("show inventory")
        print(f"{device} show inventory: {show_inventory[device]}")
        
    # Disconnect from network devices
    for device in testbed.devices:
        print(f"Disconnecting from device {device}.")
        testbed.devices[device].disconnect()
    
    # Built inventory report over data structure

    # Generate a CSV File of data
  
```

CLI:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml `

```bash
(inventory)  devnet@Devnet  ~/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON   main ±  ./network_inventory_03.py nso_sandbox_testbed_same_credentials.yaml    
####################################
Creating a Network Inventory script.
####################################
Loading testbed file: nso_sandbox_testbed_same_credentials.yaml
Enter default password for testbed: 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: 
Connecting to all devices in testbed: nso_sandbox_testbed_same_credentials

Gatherin show version from device core-rtr01
core-rtr01 show version: {'operating_system': 'IOSXR', 'software_version': '6.3.1', 'uptime': '2 days, 2 hours, 19 minutes', 'image': 'bootflash:disk0/xrvr-os-mbi-6.3.1/mbixrvr-rp.vm', 'device_family': 'IOS XRv Series', 'processor': 'Pentium II Stepping 7', 'processor_memory_bytes': '3145215K', 'main_mem': 'cisco IOS XRv Series (Pentium II Stepping 7) processor with 3145215K bytes of memory.', 'chassis_detail': 'IOS XRv Chassis', 'config_register': '0x2102', 'rp_config_register': '0x2102'}
Gatherin show inventory from device core-rtr01
core-rtr01 show inventory: {'module_name': {'0/0/CPU0': {'descr': 'Route Processor type (16, 0)', 'pid': 'IOSXRV', 'vid': 'V01', 'sn': 'N/A'}}}
```
## ERROR GATHERING INFO "ASA"

In this type of scenario is necesary to user regular expresion (RegEx), str.find(), TextFSM.

```bash
Gatherin show version from device edge-firewall01
Traceback (most recent call last):
  File "/home/devnet/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/./network_inventory_03.py", line 40, in <module>
    show_version[device] = testbed.devices[device].parse("show version")
  File "src/genie/conf/base/device.py", line 531, in genie.conf.base.device.Device.parse
  File "src/genie/conf/base/device.py", line 570, in genie.conf.base.device.Device._get_parser_output
  File "src/genie/conf/base/device.py", line 568, in genie.conf.base.device.Device._get_parser_output
  File "src/genie/metaparser/_metaparser.py", line 342, in genie.metaparser._metaparser.MetaParser.parse
  File "src/genie/metaparser/_metaparser.py", line 322, in genie.metaparser._metaparser.MetaParser.parse
  File "src/genie/metaparser/util/schemaengine.py", line 419, in genie.metaparser.util.schemaengine.Schema.validate
genie.metaparser.util.exceptions.SchemaMissingKeyError: Missing keys: [['version', 'mem_size'], ['version', 'platform'], ['version', 'processor_type']]

```
![image](https://user-images.githubusercontent.com/38144008/222665998-f9762020-a77c-402a-9aa1-4c76a1091ee3.png)

# HANDLING ERRORS IN PYTHON

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

In this section we are resolving the exception that was generated previously.

```python
genie.metaparser.util.exceptions.SchemaMissingKeyError: Missing keys: [['version', 'mem_size'], ['version', 'platform'], ['version', 'processor_type']] 
```
to resolve that issue we are going to issue exceptions like this.

```python

    def parse_command(device, command):
        """
        Attempt to parse a command on a device with PyATS.
        In caase of common errors, return best info possible.
        """
        print(f"Running {command} on {device.name}")
        try:
            output = device.parse(command)
            return {"type":"parsed", "output": output}
        except ParserNotFound:
            print(f"\033[91mError: pyATS lacks a parser for device\033[0m")
        except SchemaMissingKeyError:
            print(f"\033[91mError: pyATS lacks missing keys for device\033[0m")
            
```
![image](https://user-images.githubusercontent.com/38144008/222838603-e211d307-3ba8-45c7-948d-1bcc04e20d57.png)

However as a result of this code we have this type of error that is little different.

```bash

Gathering show version from device edge-sw01
Running show version on edge-sw01
edge-sw01 show version: {'type': 'parsed', 'output': {'version': {'version_short': '15.2', 'platform': 'vios_l2', 'version': '15.2(20200924:215240)', 'image_id': 'vios_l2-ADVENTERPRISEK9-M', 'label': '[sweickge-sep24-2020-l2iol-release 135]', 'os': 'IOS', 'image_type': 'developer image', 'copyright_years': '1986-2020', 'compiled_date': 'Tue 29-Sep-20 11:53', 'compiled_by': 'sweickge', 'rom': 'Bootstrap program is IOSv', 'hostname': 'edge-sw01', 'uptime': '2 days, 16 hours, 4 minutes', 'returned_to_rom_by': 'reload', 'system_image': 'flash0:/vios_l2-adventerprisek9-m', 'last_reload_reason': 'Unknown reason', 'chassis': 'IOSv', 'main_mem': '722145', 'processor_type': '', 'rtr_type': 'IOSv', 'chassis_sn': '9JKJJ4YUDOL', 'number_of_intfs': {'Gigabit Ethernet': '4'}, 'mem_size': {'non-volatile configuration': '256'}, 'processor_board_flash': '0K', 'curr_config_register': '0x101'}}}

Gathering show inventory from device edge-sw01
Running show inventory on edge-sw01
Traceback (most recent call last):
  File "/home/devnet/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/./network_inventory.py", line 63, in <module>
    show_inventory[device] = parse_command(testbed.devices[device], "show inventory")
  File "/home/devnet/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/./network_inventory.py", line 46, in parse_command
    output = device.parse(command)
  File "src/genie/conf/base/device.py", line 531, in genie.conf.base.device.Device.parse
  File "src/genie/conf/base/device.py", line 570, in genie.conf.base.device.Device._get_parser_output
  File "src/genie/conf/base/device.py", line 568, in genie.conf.base.device.Device._get_parser_output
  File "src/genie/metaparser/_metaparser.py", line 329, in genie.metaparser._metaparser.MetaParser.parse
  File "src/genie/metaparser/_metaparser.py", line 322, in genie.metaparser._metaparser.MetaParser.parse
  File "src/genie/metaparser/util/schemaengine.py", line 233, in genie.metaparser.util.schemaengine.Schema.validate
genie.metaparser.util.exceptions.SchemaEmptyParserError: Parser Output is empty
```
![image](https://user-images.githubusercontent.com/38144008/222838581-f8bbf2f1-25a3-4b3c-9642-38300d0c5eff.png)

That make sense is empty when insert `show inventory`.

![image](https://user-images.githubusercontent.com/38144008/222839736-3c64ed17-8eac-46f7-a53b-48eddaf17a82.png)

In this case we need to add an other exception in order to continue the process.

```python
 def parse_command(device, command):
        """
        Attempt to parse a command on a device with PyATS.
        In caase of common errors, return best info possible.
        """
        print(f"Running {command} on {device.name}")
        try:
            output = device.parse(command)
            return {"type":"parsed", "output": output}
        except ParserNotFound:
            print(f"\033[91mError: pyATS lacks a parser for device\033[0m")
        except SchemaMissingKeyError:
            print(f"\033[91mError: pyATS lacks missing keys for device\033[0m")
        except SchemaEmptyParserError:
            print(f"\033[91mError: No valid data found in the device\033[0m")
            
        # device.execute runs command, gathers raw output
        output = device.execute(command)
        return {"type":"raw", "output":output}
```

![image](https://user-images.githubusercontent.com/38144008/222843921-053aa549-f04d-42b5-abf5-cb2e2e31a0ec.png)

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

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

Gathering show version from device core-rtr01
Running show version on core-rtr01
core-rtr01 show version: {'type': 'parsed', 'output': {'operating_system': 'IOSXR', 'software_version': '6.3.1', 'uptime': '2 days, 17 hours, 18 minutes', 'image': 'bootflash:disk0/xrvr-os-mbi-6.3.1/mbixrvr-rp.vm', 'device_family': 'IOS XRv Series', 'processor': 'Pentium II Stepping 7', 'processor_memory_bytes': '3145215K', 'main_mem': 'cisco IOS XRv Series (Pentium II Stepping 7) processor with 3145215K bytes of memory.', 'chassis_detail': 'IOS XRv Chassis', 'config_register': '0x2102', 'rp_config_register': '0x2102'}}

Gathering show inventory from device core-rtr01
Running show inventory on core-rtr01
core-rtr01 show inventory: {'type': 'parsed', 'output': {'module_name': {'0/0/CPU0': {'descr': 'Route Processor type (16, 0)', 'pid': 'IOSXRV', 'vid': 'V01', 'sn': 'N/A'}}}}

Gathering show version from device core-rtr02
Running show version on core-rtr02
core-rtr02 show version: {'type': 'parsed', 'output': {'operating_system': 'IOSXR', 'software_version': '6.3.1', 'uptime': '2 days, 17 hours, 18 minutes', 'image': 'bootflash:disk0/xrvr-os-mbi-6.3.1/mbixrvr-rp.vm', 'device_family': 'IOS XRv Series', 'processor': 'Pentium II Stepping 7', 'processor_memory_bytes': '3145215K', 'main_mem': 'cisco IOS XRv Series (Pentium II Stepping 7) processor with 3145215K bytes of memory.', 'chassis_detail': 'IOS XRv Chassis', 'config_register': '0x2102', 'rp_config_register': '0x2102'}}

Gathering show inventory from device core-rtr02
Running show inventory on core-rtr02
core-rtr02 show inventory: {'type': 'parsed', 'output': {'module_name': {'0/0/CPU0': {'descr': 'Route Processor type (16, 0)', 'pid': 'IOSXRV', 'vid': 'V01', 'sn': 'N/A'}}}}

Gathering show version from device dist-rtr01
Running show version on dist-rtr01
dist-rtr01 show version: {'type': 'parsed', 'output': {'version': {'xe_version': '17.03.02', 'version_short': '17.3', 'platform': 'Virtual XE', 'version': '17.3.2', 'image_id': 'X86_64_LINUX_IOSD-UNIVERSALK9-M', 'label': 'RELEASE SOFTWARE (fc3)', 'os': 'IOS-XE', 'location': 'Amsterdam', 'image_type': 'production image', 'copyright_years': '1986-2020', 'compiled_date': 'Sat 31-Oct-20 13:16', 'compiled_by': 'mcpre', 'rom': 'IOS-XE ROMMON', 'hostname': 'dist-rtr01', 'uptime': '2 days, 17 hours, 16 minutes', 'uptime_this_cp': '2 days, 17 hours, 18 minutes', 'returned_to_rom_by': 'reload', 'system_image': 'bootflash:packages.conf', 'last_reload_reason': 'reload', 'license_level': 'ax', 'license_type': 'N/A(Smart License Enabled)', 'next_reload_license_level': 'ax', 'chassis': 'CSR1000V', 'main_mem': '1105351', 'processor_type': 'VXE', 'rtr_type': 'CSR1000V', 'chassis_sn': '91EDY6XXOPI', 'router_operating_mode': 'Autonomous', 'number_of_intfs': {'Gigabit Ethernet': '6'}, 'mem_size': {'non-volatile configuration': '32768', 'physical': '3012036'}, 'disks': {'bootflash:.': {'disk_size': '6188032', 'type_of_disk': 'virtual hard disk'}}, 'curr_config_register': '0x2102'}}}

Gathering show inventory from device dist-rtr01
Running show inventory on dist-rtr01
dist-rtr01 show inventory: {'type': 'parsed', 'output': {'main': {'chassis': {'CSR1000V': {'name': 'Chassis', 'descr': 'Cisco CSR1000V Chassis', 'pid': 'CSR1000V', 'vid': 'V00', 'sn': '91EDY6XXOPI'}}}, 'slot': {'R0': {'rp': {'CSR1000V': {'name': 'module R0', 'descr': 'Cisco CSR1000V Route Processor', 'pid': 'CSR1000V', 'vid': 'V00', 'sn': 'JAB1303001C'}}}, 'F0': {'other': {'CSR1000V': {'name': 'module F0', 'descr': 'Cisco CSR1000V Embedded Services Processor', 'pid': 'CSR1000V', 'vid': '', 'sn': ''}}}}}}

Gathering show version from device dist-rtr02
Running show version on dist-rtr02
dist-rtr02 show version: {'type': 'parsed', 'output': {'version': {'xe_version': '17.03.02', 'version_short': '17.3', 'platform': 'Virtual XE', 'version': '17.3.2', 'image_id': 'X86_64_LINUX_IOSD-UNIVERSALK9-M', 'label': 'RELEASE SOFTWARE (fc3)', 'os': 'IOS-XE', 'location': 'Amsterdam', 'image_type': 'production image', 'copyright_years': '1986-2020', 'compiled_date': 'Sat 31-Oct-20 13:16', 'compiled_by': 'mcpre', 'rom': 'IOS-XE ROMMON', 'hostname': 'dist-rtr02', 'uptime': '2 days, 17 hours, 16 minutes', 'uptime_this_cp': '2 days, 17 hours, 18 minutes', 'returned_to_rom_by': 'reload', 'system_image': 'bootflash:packages.conf', 'last_reload_reason': 'reload', 'license_level': 'ax', 'license_type': 'N/A(Smart License Enabled)', 'next_reload_license_level': 'ax', 'chassis': 'CSR1000V', 'main_mem': '1105351', 'processor_type': 'VXE', 'rtr_type': 'CSR1000V', 'chassis_sn': '9X9NDJ21PR5', 'router_operating_mode': 'Autonomous', 'number_of_intfs': {'Gigabit Ethernet': '6'}, 'mem_size': {'non-volatile configuration': '32768', 'physical': '3012036'}, 'disks': {'bootflash:.': {'disk_size': '6188032', 'type_of_disk': 'virtual hard disk'}}, 'curr_config_register': '0x2102'}}}

Gathering show inventory from device dist-rtr02
Running show inventory on dist-rtr02
dist-rtr02 show inventory: {'type': 'parsed', 'output': {'main': {'chassis': {'CSR1000V': {'name': 'Chassis', 'descr': 'Cisco CSR1000V Chassis', 'pid': 'CSR1000V', 'vid': 'V00', 'sn': '9X9NDJ21PR5'}}}, 'slot': {'R0': {'rp': {'CSR1000V': {'name': 'module R0', 'descr': 'Cisco CSR1000V Route Processor', 'pid': 'CSR1000V', 'vid': 'V00', 'sn': 'JAB1303001C'}}}, 'F0': {'other': {'CSR1000V': {'name': 'module F0', 'descr': 'Cisco CSR1000V Embedded Services Processor', 'pid': 'CSR1000V', 'vid': '', 'sn': ''}}}}}}

Gathering show version from device dist-sw01
Running show version on dist-sw01
dist-sw01 show version: {'type': 'parsed', 'output': {'platform': {'name': 'Nexus', 'os': 'NX-OS', 'software': {'system_version': '9.2(4)', 'system_image_file': 'bootflash:///nxos.9.2.4.bin', 'system_compile_time': '8/20/2019 7:00:00 [08/20/2019 15:52:22]'}, 'hardware': {'model': 'Nexus9000 9000v', 'chassis': 'Nexus9000 9000v', 'slots': 'None', 'rp': 'None', 'cpu': 'Intel(R) Xeon(R) Gold 6238 CPU @ 2.10GHz', 'memory': '8161516 kB', 'processor_board_id': '9ORBHMVBPDB', 'device_name': 'dist-sw01', 'bootflash': '3509454 kB'}, 'kernel_uptime': {'days': 2, 'hours': 17, 'minutes': 16, 'seconds': 14}, 'reason': 'Unknown'}}}

Gathering show inventory from device dist-sw01
Running show inventory on dist-sw01
dist-sw01 show inventory: {'type': 'parsed', 'output': {'name': {'Chassis': {'description': 'Nexus9000 9000v Chassis', 'slot': 'None', 'pid': 'N9K-9000v', 'vid': 'V02', 'serial_number': '9ORBHMVBPDB'}, 'Slot 1': {'description': 'Nexus 9000v Ethernet Module', 'slot': '1', 'pid': 'N9K-9000v', 'vid': 'V02', 'serial_number': '9ORBHMVBPDB'}, 'Fan 1': {'description': 'Nexus9000 9000v Chassis Fan Module', 'slot': 'None', 'pid': 'N9K-9000v-FAN', 'vid': 'V01', 'serial_number': 'N/A'}, 'Fan 2': {'description': 'Nexus9000 9000v Chassis Fan Module', 'slot': 'None', 'pid': 'N9K-9000v-FAN', 'vid': 'V01', 'serial_number': 'N/A'}, 'Fan 3': {'description': 'Nexus9000 9000v Chassis Fan Module', 'slot': 'None', 'pid': 'N9K-9000v-FAN', 'vid': 'V01', 'serial_number': 'N/A'}}}}

Gathering show version from device dist-sw02
Running show version on dist-sw02
dist-sw02 show version: {'type': 'parsed', 'output': {'platform': {'name': 'Nexus', 'os': 'NX-OS', 'software': {'system_version': '9.2(4)', 'system_image_file': 'bootflash:///nxos.9.2.4.bin', 'system_compile_time': '8/20/2019 7:00:00 [08/20/2019 15:52:22]'}, 'hardware': {'model': 'Nexus9000 9000v', 'chassis': 'Nexus9000 9000v', 'slots': 'None', 'rp': 'None', 'cpu': 'Intel(R) Xeon(R) Gold 6238 CPU @ 2.10GHz', 'memory': '8161516 kB', 'processor_board_id': '9NLTHFK2289', 'device_name': 'dist-sw02', 'bootflash': '3509454 kB'}, 'kernel_uptime': {'days': 2, 'hours': 17, 'minutes': 16, 'seconds': 11}, 'reason': 'Unknown'}}}

Gathering show inventory from device dist-sw02
Running show inventory on dist-sw02
dist-sw02 show inventory: {'type': 'parsed', 'output': {'name': {'Chassis': {'description': 'Nexus9000 9000v Chassis', 'slot': 'None', 'pid': 'N9K-9000v', 'vid': 'V02', 'serial_number': '9NLTHFK2289'}, 'Slot 1': {'description': 'Nexus 9000v Ethernet Module', 'slot': '1', 'pid': 'N9K-9000v', 'vid': 'V02', 'serial_number': '9NLTHFK2289'}, 'Fan 1': {'description': 'Nexus9000 9000v Chassis Fan Module', 'slot': 'None', 'pid': 'N9K-9000v-FAN', 'vid': 'V01', 'serial_number': 'N/A'}, 'Fan 2': {'description': 'Nexus9000 9000v Chassis Fan Module', 'slot': 'None', 'pid': 'N9K-9000v-FAN', 'vid': 'V01', 'serial_number': 'N/A'}, 'Fan 3': {'description': 'Nexus9000 9000v Chassis Fan Module', 'slot': 'None', 'pid': 'N9K-9000v-FAN', 'vid': 'V01', 'serial_number': 'N/A'}}}}

Gathering show version from device edge-firewall01
Running show version on edge-firewall01
Error: pyATS lacks missing keys for device
edge-firewall01 show version: {'type': 'raw', 'output': '\r\nCisco Adaptive Security Appliance Software Version 9.15(1)1 \r\nSSP Operating System Version 2.9(1.131)\r\nDevice Manager Version 7.15(1)\r\n\r\nCompiled on Fri 20-Nov-20 18:48 GMT by builders\r\nSystem image file is "boot:/asa9151-1-smp-k8.bin"\r\nConfig file at boot was "startup-config"\r\n\r\nedge-firewall01 up 2 days 17 hours\r\n\r\nHardware:   ASAv, 2048 MB RAM, CPU Xeon 4100/6100/8100 series 2100 MHz,\r\nInternal ATA Compact Flash, 8192MB\r\nSlot 1: ATA Compact Flash, 8192MB\r\nBIOS Flash Firmware Hub @ 0x1, 0KB\r\n\r\n\r\n 0: Ext: Management0/0       : address is 5254.000d.3e62, irq 10\r\n 1: Ext: GigabitEthernet0/0  : address is 5254.0014.a580, irq 11\r\n 2: Ext: GigabitEthernet0/1  : address is 5254.000e.f45b, irq 11\r\n 3: Int: Internal-Data0/0    : address is 0000.0100.0001, irq 0\r\n\r\nLicense mode: Smart Licensing\r\nASAv Platform License State: Unlicensed\r\nActive entitlement: ASAv-STD-1G, enforce mode: Eval period\r\nFirewall throughput limited to 100 Kbps\r\n\r\nLicensed features for this platform:\r\nMaximum VLANs                     : 50             \r\nInside Hosts                      : Unlimited      \r\nFailover                          : Active/Active  \r\nEncryption-DES                    : Enabled        \r\nEncryption-3DES-AES               : Enabled        \r\nSecurity Contexts                 : 2              \r\nCarrier                           : Disabled       \r\nAnyConnect Premium Peers          : 2              \r\nAnyConnect Essentials             : Disabled       \r\nOther VPN Peers                   : 250            \r\nTotal VPN Peers                   : 250            \r\nAnyConnect for Mobile             : Disabled       \r\nAnyConnect for Cisco VPN Phone    : Disabled       \r\nAdvanced Endpoint Assessment      : Disabled       \r\nShared License                    : Disabled       \r\nTotal TLS Proxy Sessions          : 2              \r\nBotnet Traffic Filter             : Enabled        \r\nCluster                           : Disabled       \r\n\r\nSerial Number: 9A3LTK7V6RD\r\n\r\nImage type          : Release\r\nKey version         : A\r\n\r\nConfiguration has not been modified since last system restart.'}

Gathering show inventory from device edge-firewall01
Running show inventory on edge-firewall01
edge-firewall01 show inventory: {'type': 'parsed', 'output': {'Chassis': {'description': 'ASAv Adaptive Security Virtual Appliance', 'pid': 'ASAv', 'vid': 'V01', 'sn': '9A3LTK7V6RD'}}}

Gathering show version from device edge-sw01
Running show version on edge-sw01
edge-sw01 show version: {'type': 'parsed', 'output': {'version': {'version_short': '15.2', 'platform': 'vios_l2', 'version': '15.2(20200924:215240)', 'image_id': 'vios_l2-ADVENTERPRISEK9-M', 'label': '[sweickge-sep24-2020-l2iol-release 135]', 'os': 'IOS', 'image_type': 'developer image', 'copyright_years': '1986-2020', 'compiled_date': 'Tue 29-Sep-20 11:53', 'compiled_by': 'sweickge', 'rom': 'Bootstrap program is IOSv', 'hostname': 'edge-sw01', 'uptime': '2 days, 17 hours, 12 minutes', 'returned_to_rom_by': 'reload', 'system_image': 'flash0:/vios_l2-adventerprisek9-m', 'last_reload_reason': 'Unknown reason', 'chassis': 'IOSv', 'main_mem': '722145', 'processor_type': '', 'rtr_type': 'IOSv', 'chassis_sn': '9JKJJ4YUDOL', 'number_of_intfs': {'Gigabit Ethernet': '4'}, 'mem_size': {'non-volatile configuration': '256'}, 'processor_board_flash': '0K', 'curr_config_register': '0x101'}}}

Gathering show inventory from device edge-sw01
Running show inventory on edge-sw01
Error: No valid data found in the device
edge-sw01 show inventory: {'type': 'raw', 'output': ''}

Gathering show version from device internet-rtr01
Running show version on internet-rtr01
internet-rtr01 show version: {'type': 'parsed', 'output': {'version': {'xe_version': '17.03.02', 'version_short': '17.3', 'platform': 'Virtual XE', 'version': '17.3.2', 'image_id': 'X86_64_LINUX_IOSD-UNIVERSALK9-M', 'label': 'RELEASE SOFTWARE (fc3)', 'os': 'IOS-XE', 'location': 'Amsterdam', 'image_type': 'production image', 'copyright_years': '1986-2020', 'compiled_date': 'Sat 31-Oct-20 13:16', 'compiled_by': 'mcpre', 'rom': 'IOS-XE ROMMON', 'hostname': 'internet-rtr01', 'uptime': '2 days, 17 hours, 17 minutes', 'uptime_this_cp': '2 days, 17 hours, 18 minutes', 'returned_to_rom_by': 'reload', 'system_image': 'bootflash:packages.conf', 'last_reload_reason': 'reload', 'license_level': 'ax', 'license_type': 'N/A(Smart License Enabled)', 'next_reload_license_level': 'ax', 'chassis': 'CSR1000V', 'main_mem': '2070983', 'processor_type': 'VXE', 'rtr_type': 'CSR1000V', 'chassis_sn': '9150TDM5N31', 'router_operating_mode': 'Autonomous', 'number_of_intfs': {'Gigabit Ethernet': '4'}, 'mem_size': {'non-volatile configuration': '32768', 'physical': '3978236'}, 'disks': {'bootflash:.': {'disk_size': '6188032', 'type_of_disk': 'virtual hard disk'}}, 'curr_config_register': '0x2102'}}}

Gathering show inventory from device internet-rtr01
Running show inventory on internet-rtr01
internet-rtr01 show inventory: {'type': 'parsed', 'output': {'main': {'chassis': {'CSR1000V': {'name': 'Chassis', 'descr': 'Cisco CSR1000V Chassis', 'pid': 'CSR1000V', 'vid': 'V00', 'sn': '9150TDM5N31'}}}, 'slot': {'R0': {'rp': {'CSR1000V': {'name': 'module R0', 'descr': 'Cisco CSR1000V Route Processor', 'pid': 'CSR1000V', 'vid': 'V00', 'sn': 'JAB1303001C'}}}, 'F0': {'other': {'CSR1000V': {'name': 'module F0', 'descr': 'Cisco CSR1000V Embedded Services Processor', 'pid': 'CSR1000V', 'vid': '', 'sn': ''}}}}}}
Disconnecting from device core-rtr01.
Disconnecting from device core-rtr02.
Disconnecting from device dist-rtr01.
Disconnecting from device dist-rtr02.
Disconnecting from device dist-sw01.
Disconnecting from device dist-sw02.
Disconnecting from device edge-firewall01.
Disconnecting from device edge-sw01.
Disconnecting from device internet-rtr01.

```
# COLLECTING DATA FOR INVENTORY REPORT

We are going to collet data as software version, uptime, serial number.

With this validate format online you can verify the json data.

+ https://www.freeformatter.com/json-validator.html

Format JSON:

```json
{
	'type': 'parsed',
	'output': {
		'operating_system': 'IOSXR',
		'software_version': '6.3.1',
		'uptime': '2 days, 17 hours, 18 minutes',
		'image': 'bootflash:disk0/xrvr-os-mbi-6.3.1/mbixrvr-rp.vm',
		'device_family': 'IOS XRv Series',
		'processor': 'Pentium II Stepping 7',
		'processor_memory_bytes': '3145215K',
		'main_mem': 'cisco IOS XRv Series (Pentium II Stepping 7) processor with 3145215K bytes of memory.',
		'chassis_detail': 'IOS XRv Chassis',
		'config_register': '0x2102',
		'rp_config_register': '0x2102'
	}
}

{
	'type': 'parsed',
	'output': {
		'module_name': {
			'0/0/CPU0': {
				'descr': 'Route Processor type (16, 0)',
				'pid': 'IOSXRV',
				'vid': 'V01',
				'sn': 'N/A'
			}
		}
	}
}
```

After that we need to collect the information:

```python
# Built inventory report over data structure
    #   IOS XR
    #       software_version: show version output ["output"]["software version"]
    #       uptime:           show version output ["output"]["uptime"]
    #       serial:           show inventory output ["output"]["module_name"]["MODULE"]["sn"]    
    #
    #
    #

    def get_devices_inventory(device, show_version, show_inventory):
        # Common detail from tested device
        device_name = device.name
        device_os = device.os

        if device_os in ["ios","iosxe","nxos","iosxr","asa"]:
            software_version = None
            uptime = None
            serial_number = None
        else:
            return False
        
        return (device_name, device_os, software_version, uptime, serial_number)
    
    print(f"\n\033[92mAssembling network inventory data from output.\033[0m")
    
    network_inventory = []
    
    for device in testbed.devices:
        network_inventory.append(
            get_devices_inventory(
                testbed.devices[device],
                show_version, 
                show_inventory)
                )
    
    print(f"\n\033[92mnetwork_inventory = {network_inventory}\033[0m")
    
```

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

![image](https://user-images.githubusercontent.com/38144008/222874016-1441c9f4-6cf3-4dfe-a579-a3ab4cd329c8.png)


+ In this section we are going to add all the elements, and let´s to resolve with regular expresion certain parameters that you see in "None" in this phase.

Code that permit filter the parameters required to diplay the network inventory.

```python
# Built inventory report over data structure
    #   IOS XR
    #       software_version: show version output ["output"]["software_version"]
    #       uptime:           show version output ["output"]["uptime"]
    #       sn:               show inventory output ["output"]["module_name"]["MODULE"]["sn"]    
    #
    #   IOS-XE
    #       xe_version:       show version output ["output"]["version"]["xe_version"]
    #       uptime:           show version output ["output"]["version"]["uptime"]
    #       sn:               show inventory output ["output"]["main"]["chassis"]["CSR1000V"]["sn"]
    #  
    #   IOS
    #       version:          show version output ["output"]["version"]["version"]
    #       uptime:           show version output ["output"]["version"]["uptime"]
    #       serial:N/A        show inventory output ["output"]
    #
    #   NX-OS
    #       system_version:   show version output ["output"]["platform"]["software"]["system_version"] 
    #       kernel_uptime:    show version output ["output"]["platform"]["kernel_uptime"]  
    #       serial_number:    show inventory output ["output"]["name"]["Chassis"]["serial_number"]  
    #   
    #   ASA
    #       software_version: show version output ["output"] "Cisco Adaptive Security Appliance Software Version 9.15(1)1"
    #       uptime:           show version output ["output"] "up 2 days 17 hours"  
    #       sn:               show inventory output ["output"]["Chassis"]["sn"]  
    #

    def get_devices_inventory(device, show_version, show_inventory):
        # Common detail from tested device
        device_name = device.name
        device_os = device.os

        if device.os == "ios":
            software_version = show_version[device.name]["output"]["version"]["version"]
            uptime = show_version[device_name]["output"]["version"]["uptime"]
            serial_number = None
        elif device.os == "iosxe":
            software_version = show_version[device.name]["output"]["version"]["xe_version"]
            uptime = show_version[device_name]["output"]["version"]["uptime"]
            serial_number = None
        elif device.os == "nxos":
            software_version = show_version[device.name]["output"]["platform"]["software"]["system_version"]
            uptime = show_version[device.name]["output"]["platform"]["kernel_uptime"]
            serial_number = show_inventory[device.name]["output"]["name"]["Chassis"]["serial_number"]
        elif device.os == "iosxr":
            software_version = show_version[device.name]["output"]["software_version"]
            uptime = show_version[device.name]["output"]["uptime"]
            serial_number = None
        elif device.os == "asa":
            software_version = None
            uptime = None
            serial_number = show_inventory[device.name]["output"]["Chassis"]["sn"]
        else:
            return False
        
        return (device_name, device_os, software_version, uptime, serial_number)
    
    print(f"\n\033[92mAssembling network inventory data from output.\033[0m")
    
    network_inventory = []
    
    for device in testbed.devices:
        network_inventory.append(
            get_devices_inventory(
                testbed.devices[device],
                show_version, 
                show_inventory)
                )
    
    print(f"\n\033[96mnetwork_inventory = {network_inventory}\033[0m")
    

```

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

The parameter serial_number is None. Output:

```json

Assembling network inventory.

network_inventory = [('core-rtr01', 'iosxr', '6.3.1', '2 days, 21 hours, 38 minutes', None), ('core-rtr02', 'iosxr', '6.3.1', '2 days, 21 hours, 38 minutes', None), ('dist-rtr01', 'iosxe', '17.03.02', '2 days, 21 hours, 37 minutes', None), ('dist-rtr02', 'iosxe', '17.03.02', '2 days, 21 hours, 36 minutes', None), ('dist-sw01', 'nxos', '9.2(4)', {'days': 2, 'hours': 21, 'minutes': 36, 'seconds': 28}, '9ORBHMVBPDB'), ('dist-sw02', 'nxos', '9.2(4)', {'days': 2, 'hours': 21, 'minutes': 36, 'seconds': 25}, '9NLTHFK2289'), ('edge-firewall01', 'asa', None, None, '9A3LTK7V6RD'), ('edge-sw01', 'ios', '15.2(20200924:215240)', '2 days, 21 hours, 32 minutes', None), ('internet-rtr01', 'iosxe', '17.03.02', '2 days, 21 hours, 37 minutes', None)]
```
![image](https://user-images.githubusercontent.com/38144008/222873996-a26acb13-5b00-45b4-abcc-93f01c3ac843.png)

# FIX SERIAL NUMBER 

+ In this section we are going to add all the elements, and let´s to resolve with regular expresion certain parameters that you see in "None" in this phase.

Code that permit filter the parameters required to diplay the network inventory.

```python

    # Built inventory report over data structure
    #   IOS XR
    #       software_version: show version output ["output"]["software_version"]
    #       uptime:           show version output ["output"]["uptime"]
    #       sn:               show inventory output ["output"]["module_name"]["MODULE"]["sn"]    
    #
    #   IOS-XE
    #       xe_version:       show version output ["output"]["version"]["xe_version"]
    #       uptime:           show version output ["output"]["version"]["uptime"]
    #       sn:               show inventory output ["output"]["main"]["chassis"]["CSR1000V"]["sn"]
    #  
    #   IOS
    #       version:          show version output ["output"]["version"]["version"]
    #       uptime:           show version output ["output"]["version"]["uptime"]
    #       serial:N/A        show inventory output ["output"]
    #
    #   NX-OS
    #       system_version:   show version output ["output"]["platform"]["software"]["system_version"] 
    #       kernel_uptime:    show version output ["output"]["platform"]["kernel_uptime"]  
    #       serial_number:    show inventory output ["output"]["name"]["Chassis"]["serial_number"]  
    #   
    #   ASA
    #       software_version: show version output ["output"] "Cisco Adaptive Security Appliance Software Version 9.15(1)1"
    #       uptime:           show version output ["output"] "up 2 days 17 hours"  
    #       sn:               show inventory output ["output"]["Chassis"]["sn"]  
    #

    def get_devices_inventory(device, show_version, show_inventory):
        # Common detail from tested device
        device_name = device.name
        device_os = device.os

        if device.os in ["ios","iosxe"]:
            software_version = show_version[device.name]["output"]["version"]["version"]
            uptime = show_version[device_name]["output"]["version"]["uptime"]
            # Skip devices without parsed show inventory data
            if show_inventory[device.name]["output"] !="":
                # Extract chassi_name = 'CSR1000V' 
                chassis_name = show_version[device.name]["output"]["version"]["chassis"]
                serial_number = show_inventory[device.name]["output"]["main"]["chassis"][chassis_name]["sn"]
            else:
                serial_number = "N/A"    
        elif device.os == "nxos":
            software_version = show_version[device.name]["output"]["platform"]["software"]["system_version"]
            uptime_dict = show_version[device.name]["output"]["platform"]["kernel_uptime"]
            uptime = f'{uptime_dict["days"]} days, {uptime_dict["hours"]} hours,{uptime_dict["minutes"]} minutes'
            serial_number = show_inventory[device.name]["output"]["name"]["Chassis"]["serial_number"]
        elif device.os == "iosxr":
            software_version = show_version[device.name]["output"]["software_version"]
            uptime = show_version[device.name]["output"]["uptime"]
                        
            # Grab the serial from first module - should be the RP
            # Mapping all content in module_name and capture module["sn"] as serial_number
            for module in show_inventory[device.name]["output"]["module_name"].values():
                serial_number = module["sn"]
                break

        elif device.os == "asa":
            software_version = None
            uptime = None
            serial_number = show_inventory[device.name]["output"]["Chassis"]["sn"]
        else:
            return False
        
        return (device_name, device_os, software_version, uptime, serial_number)
    
    print(f"\n\033[92mAssembling network inventory data from output.\033[0m")
    
    network_inventory = []
    
    for device in testbed.devices:
        network_inventory.append(
            get_devices_inventory(
                testbed.devices[device],
                show_version, 
                show_inventory)
                )
    
    print(f"\n\033[97mnetwork_inventory = {network_inventory}\033[0m")
    
```

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

```json
Assembling network inventory data from output.

network_inventory = [('core-rtr01', 'iosxr', '6.3.1', '2 days, 22 hours, 53 minutes', 'N/A'), ('core-rtr02', 'iosxr', '6.3.1', '2 days, 22 hours, 53 minutes', 'N/A'), ('dist-rtr01', 'iosxe', '17.3.2', '2 days, 22 hours, 51 minutes', '91EDY6XXOPI'), ('dist-rtr02', 'iosxe', '17.3.2', '2 days, 22 hours, 51 minutes', '9X9NDJ21PR5'), ('dist-sw01', 'nxos', '9.2(4)', '2 days, 22 hours,51 minutes', '9ORBHMVBPDB'), ('dist-sw02', 'nxos', '9.2(4)', '2 days, 22 hours,50 minutes', '9NLTHFK2289'), ('edge-firewall01', 'asa', None, None, '9A3LTK7V6RD'), ('edge-sw01', 'ios', '15.2(20200924:215240)', '2 days, 22 hours, 46 minutes', 'N/A'), ('internet-rtr01', 'iosxe', '17.3.2', '2 days, 22 hours, 51 minutes', '9150TDM5N31')]
```

+ In this section uses regular expressions to obtain the coorect that in our ASA.

Script in Python:

```python
        elif device.os == "asa":
            software_version_regex = "Software Version ([^\n ]*)"
            uptime_regex = f"{device.name} up ([\d]* days? [\d]* hours?)"

            software_version = re.search(software_version_regex, show_version[device.name]["output"]).group(1)
            uptime = re.search(uptime_regex, show_version[device.name]["output"]).group(1)

            serial_number = show_inventory[device.name]["output"]["Chassis"]["sn"]


```

RUN CLI:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

```json
Assembling network inventory data from output.

network_inventory = [('core-rtr01', 'iosxr', '6.3.1', '3 days, 5 minutes', 'N/A'), ('core-rtr02', 'iosxr', '6.3.1', '3 days, 5 minutes', 'N/A'), ('dist-rtr01', 'iosxe', '17.3.2', '3 days, 4 minutes', '91EDY6XXOPI'), ('dist-rtr02', 'iosxe', '17.3.2', '3 days, 4 minutes', '9X9NDJ21PR5'), ('dist-sw01', 'nxos', '9.2(4)', '3 days, 0 hours,3 minutes', '9ORBHMVBPDB'), ('dist-sw02', 'nxos', '9.2(4)', '3 days, 0 hours,3 minutes', '9NLTHFK2289'), ('edge-firewall01', 'asa', '9.15(1)1', '3 days 0 hours', '9A3LTK7V6RD'), ('edge-sw01', 'ios', '15.2(20200924:215240)', '2 days, 23 hours, 59 minutes', 'N/A'), ('internet-rtr01', 'iosxe', '17.3.2', '3 days, 4 minutes', '9150TDM5N31')]
```

# CREATING A CSV FILE

In this section using la library csv are generating the csv file.

RUN CLI: `/network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

```python
    # Generate a CSV File of data

    now = datetime.now()
    inventory_file = f'{now.strftime("%Y-%m-%d-%H-%M-%S")}_{testbed.name}_network_inventory.csv'
    
    print(f'Writting inventory to file {inventory_file}.')

    with open(inventory_file, 'w', newline='') as csvfile:
        inv_writer = csv.writer(csvfile, dialect="excel")
        # Write header row
        inv_writer.writerow(
            ("device_name", 
             "device_os", 
             "software_version", 
             "uptime", 
             "serial_number"
            ))
        for device in network_inventory:
            inv_writer.writerow(device)
    
```
That is the final result we have a csv file with the devices.

```json
Assembling network inventory data from output.

network_inventory = [('core-rtr01', 'iosxr', '6.3.1', '3 days, 37 minutes', 'N/A'), ('core-rtr02', 'iosxr', '6.3.1', '3 days, 37 minutes', 'N/A'), ('dist-rtr01', 'iosxe', '17.3.2', '3 days, 36 minutes', '91EDY6XXOPI'), ('dist-rtr02', 'iosxe', '17.3.2', '3 days, 36 minutes', '9X9NDJ21PR5'), ('dist-sw01', 'nxos', '9.2(4)', '3 days, 0 hours,35 minutes', '9ORBHMVBPDB'), ('dist-sw02', 'nxos', '9.2(4)', '3 days, 0 hours,35 minutes', '9NLTHFK2289'), ('edge-firewall01', 'asa', '9.15(1)1', '3 days 0 hours', '9A3LTK7V6RD'), ('edge-sw01', 'ios', '15.2(20200924:215240)', '3 days, 30 minutes', 'N/A'), ('internet-rtr01', 'iosxe', '17.3.2', '3 days, 36 minutes', '9150TDM5N31')]

Writting inventory to file 2023-03-04-00-15-08_nso_sandbox_testbed_same_credentials_network_inventory.csv.
```

# REFERNCES

+ Creation from Excel File
https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file

+ SANDBOX to test owner Inventory
https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology

+ JSON to test format
https://jsonlint.com/