#!/home/devnet/Documents/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/inventory/bin/python
"""
That is an script basic that permit capture an inventory of our network 
using CLI as "show version" and "show inventory".

Goal:
 - Create a CSV inventory file over this parameters: device name, software version, uptime, serial number
"""

# Start our program from main
from pyats.topology.loader import load
from genie.libs.parser.utils.common import ParserNotFound
from genie.metaparser.util.exceptions import SchemaMissingKeyError, SchemaEmptyParserError
import re

if __name__ == "__main__":
    import argparse

    print("####################################")
    print("Creating a Network Inventory script.")
    print("####################################")

    # Load pyATS testbed
    parser = argparse.ArgumentParser(prog = 'NETWORK INVENTORY',description='General network inventory report')
    parser.add_argument('testbed', type=str, help='pyATS Testbed File')
    args = parser.parse_args()
    print(f"\033[94mLoading testbed file: {args.testbed}\033[0m")

    # Create pyATS testbed object
    testbed =load(args.testbed)
    print(f"\033[93mConnecting to all devices in testbed: {testbed.name}\033[0m")

    # Connect to network devices
    testbed.connect(log_stdout=False)
    
    # Run command to gather output from devices
    show_version={}
    show_inventory={}

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

    for device in testbed.devices:
        print(f"\n\033[92mGathering show version from device {device}\033[0m")
        show_version[device] = parse_command(testbed.devices[device], "show version")
        print(f"{device} show version: {show_version[device]}")

        print(f"\n\033[92mGathering show inventory from device {device}\033[0m")
        show_inventory[device] = parse_command(testbed.devices[device], "show inventory")
        print(f"{device} show inventory: {show_inventory[device]}")

        

    # Disconnect from network devices
    for device in testbed.devices:
        print(f"Disconnecting from device {device}.")
        testbed.devices[device].disconnect()
    
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
            software_version_regex = "Software Version ([^\n ]*)"
            uptime_regex = f"{device.name} up ([\d]* days? [\d]* hours?)"

            software_version = re.search(software_version_regex, show_version[device.name]["output"]).group(1)
            uptime = re.search(uptime_regex, show_version[device.name]["output"]).group(1)
            
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



    # Generate a CSV File of data
    

