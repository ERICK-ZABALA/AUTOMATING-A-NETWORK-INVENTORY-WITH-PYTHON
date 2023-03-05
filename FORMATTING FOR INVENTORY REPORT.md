

# FORMATTING FOR INVENTORY REPORT

We are going to collet data as software version, uptime, serial number over devices in our devnet sandbox.

We are going to do a schema that permit collect data using the online portal JSON and we are going to put in the comments in our code. Really usefull this methodology.

+ Web Page to validate format JSON https://jsonlint.com/

# FORMAT JSON

```yaml
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

```yaml
# Built inventory report over data structure
    #   IOS XR
    #       software_version: show version output ["output"]["software version"]
    #       uptime:           show version output ["output"]["uptime"]
    #       serial:           show inventory output ["output"]["module_name"]["MODULE"]["sn"]    
   

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
    
```

CLI RUN:    `./network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

```python
Assembling network inventory data from output.

network_inventory = [('core-rtr01', 'iosxr', '6.3.1', '2 days, 22 hours, 53 minutes', 'N/A'), ('core-rtr02', 'iosxr', '6.3.1', '2 days, 22 hours, 53 minutes', 'N/A'), ('dist-rtr01', 'iosxe', '17.3.2', '2 days, 22 hours, 51 minutes', '91EDY6XXOPI'), ('dist-rtr02', 'iosxe', '17.3.2', '2 days, 22 hours, 51 minutes', '9X9NDJ21PR5'), ('dist-sw01', 'nxos', '9.2(4)', '2 days, 22 hours,51 minutes', '9ORBHMVBPDB'), ('dist-sw02', 'nxos', '9.2(4)', '2 days, 22 hours,50 minutes', '9NLTHFK2289'), ('edge-firewall01', 'asa', None, None, '9A3LTK7V6RD'), ('edge-sw01', 'ios', '15.2(20200924:215240)', '2 days, 22 hours, 46 minutes', 'N/A'), ('internet-rtr01', 'iosxe', '17.3.2', '2 days, 22 hours, 51 minutes', '9150TDM5N31')]
```
![image](https://user-images.githubusercontent.com/38144008/222886594-64b00b19-0f84-4296-9cff-3fad0e3ad713.png)

+ In this section uses regular expressions (re) to obtain the coorect that in our ASA.

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

```python
Assembling network inventory data from output.

network_inventory = [('core-rtr01', 'iosxr', '6.3.1', '3 days, 5 minutes', 'N/A'), ('core-rtr02', 'iosxr', '6.3.1', '3 days, 5 minutes', 'N/A'), ('dist-rtr01', 'iosxe', '17.3.2', '3 days, 4 minutes', '91EDY6XXOPI'), ('dist-rtr02', 'iosxe', '17.3.2', '3 days, 4 minutes', '9X9NDJ21PR5'), ('dist-sw01', 'nxos', '9.2(4)', '3 days, 0 hours,3 minutes', '9ORBHMVBPDB'), ('dist-sw02', 'nxos', '9.2(4)', '3 days, 0 hours,3 minutes', '9NLTHFK2289'), ('edge-firewall01', 'asa', '9.15(1)1', '3 days 0 hours', '9A3LTK7V6RD'), ('edge-sw01', 'ios', '15.2(20200924:215240)', '2 days, 23 hours, 59 minutes', 'N/A'), ('internet-rtr01', 'iosxe', '17.3.2', '3 days, 4 minutes', '9150TDM5N31')]
```
![image](https://user-images.githubusercontent.com/38144008/222886524-67feae5b-eacb-4431-a92e-dbd9a6edd58c.png)
