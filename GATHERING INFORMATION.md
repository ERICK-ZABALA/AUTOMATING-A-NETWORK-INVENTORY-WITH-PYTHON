

# GATHERING INFORMATION - SHOW VERSION & SHOW INVENTORY

In this section, we will demonstrate how to retrieve and display the output of the "show version" and "show inventory" commands using a `Python Script`.

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
        print(f"\nGathering show version from device {device}")
        show_version[device] = testbed.devices[device].parse("show version")
        print(f"{device} show version: {show_version[device]}")

        print(f"Gathering show inventory from device {device}")
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

```yaml
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
core-rtr01 show version: {'operating_system': 'IOSXR', 'software_version': '6.3.1', 'uptime': '2 days, 2 hours, 19 minutes',
'image': 'bootflash:disk0/xrvr-os-mbi-6.3.1/mbixrvr-rp.vm', 'device_family': 'IOS XRv Series', 'processor': 'Pentium II Stepping 7',
'processor_memory_bytes': '3145215K', 'main_mem': 'cisco IOS XRv Series (Pentium II Stepping 7) processor with 3145215K bytes of memory.',
'chassis_detail': 'IOS XRv Chassis', 'config_register': '0x2102', 'rp_config_register': '0x2102'}

Gatherin show inventory from device core-rtr01
core-rtr01 show inventory: {'module_name': {'0/0/CPU0': {'descr': 'Route Processor type (16, 0)', 'pid': 'IOSXRV', 'vid': 'V01',
'sn': 'N/A'}}}
```
# FIRST ISSUE IN GATHERING INFORMATION OF "ASA" (edge-firewall01)

In this scenario, we have an exception exceptions.SchemaMissingKeyError happend when a specified schema key is missing from a parsed output. 

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

# SOLUTION FIRST ISSUE 

To resolve that issue we are going to use `exceptions` in our code in python.

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

# SECOND ISSUE IN GATHERING INFORMATION OF "edge-sw01"

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

# SOLUTION SECOND ISSUE 

In this case we need to add an other `exception` in order to continue the process.

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

# FINAL SOLUTION - GATHERING INFORMATION

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

```yaml
(inventory)  devnet@Devnet  ~/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON   main ±  ./network_inventory.py nso_sandbox_testbed_same_credentials.yaml

####################################
Creating a Network Inventory Script.
####################################
Loading testbed file: nso_sandbox_testbed_same_credentials.yaml
Enter default password for testbed: cisco 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: cisco
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
