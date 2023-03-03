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
    

