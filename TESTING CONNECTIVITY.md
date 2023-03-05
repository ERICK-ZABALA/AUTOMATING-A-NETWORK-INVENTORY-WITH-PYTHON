# TESTING CONNECTIVITY 

+ We are going to validate if CLI with PyATS works properly. 

RUN CLI:    (inventory) [opc@jenkins-master NETWORK-INVENTORY-WITH-PYTHON]$ `pyats parse "show version" --testbed nso_sandbox_testbed_same_credentials.yaml`

Here's a breakdown of the command and what each component does:

pyats: This is the command used to run PyATS.
parse: This is the PyATS sub-command used to parse the output of a show command on a network device.
"show version": This is the show command that will be executed on the network device. In this case, it will likely retrieve the device's software version information.
--testbed nso_sandbox_testbed_same_credentials.yaml: This specifies the testbed file that PyATS should use to connect to the network device and execute the show command. The testbed file is in YAML format and is named "nso_sandbox_testbed_same_credentials.yaml". The contents of the testbed file likely contain information about the network device(s) that PyATS will be connecting to, such as their IP addresses, login credentials, and other connection details.

```bash
inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls

inventory  nso_sandbox_testbed_same_credentials.yaml  nso_sandbox_testbed.yaml  README.md  sample

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

Sometimes parsers can not be included in some plataforms, that is the reason of this error in asa device.

## ERROR GENERATE IN ASA DEVICE

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

That is the information to generate us inventory report csv file.

```json
"operating_system": "IOSXR",
"software_version": "6.3.1",
"uptime": "1 day, 10 hours, 14 minutes"
```

If you PyAts parse not found the specific command "show version" you probably receive this answer.

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
# EXECUTABLE SCRIPT PYTHON

+ How to resolve this problem?

Well, the solution to this type of problem is with code in Python; Yes we need to create a script using Python.

+ Create a script in python and executable `chmod +x network_inventory.py`.

![image](https://user-images.githubusercontent.com/38144008/222495857-2ce07c78-d329-4326-8933-ac9f19b16f80.png)

```bash
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ chmod +x network_inventory.py
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  'network_inventory.py'  nso_sandbox_testbed_same_credentials.yaml  nso_sandbox_testbed.yaml  README.md  sample
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$
```
Note: Verify your `shebang` in your script in order to works properly

![image](https://user-images.githubusercontent.com/38144008/222668149-ef8217cf-c85a-478a-894d-8ca389d0c0e2.png)

# PYTHON SCRIPTING FOR NETWORK CONNECTIVITY TESTING WITH PyATS

This command `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml` permit to verify your concetivity from PyATS, script and network access.

```bash
(inventory)  devnet@Devnet  ~/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON$`./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

Creating a network inventory script.
Namespace(testbed='nso_sandbox_testbed_same_credentials.yaml')
Enter default password for testbed: 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: 
<Testbed object 'nso_sandbox_testbed_same_credentials' at 0x7fa854c41fc0>

2023-03-02 21:43:19,858: %UNICON-INFO: +++ core-rtr02 logfile /tmp/core-rtr02-cli-20230302T214319855.log +++

2023-03-02 21:43:19,861: %UNICON-INFO: +++ Unicon plugin iosxr (unicon.plugins.iosxr) +++
```

# TESTING DISABLE LOGS IN PARSER

+ Disabling logs in parser

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
# FINAL RESULT

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

```yaml
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

