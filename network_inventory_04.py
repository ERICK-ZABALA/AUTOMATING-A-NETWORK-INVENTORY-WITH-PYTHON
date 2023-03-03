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
from genie.metaparser.util.exceptions import SchemaMissingKeyError

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

    # Generate a CSV File of data
    

