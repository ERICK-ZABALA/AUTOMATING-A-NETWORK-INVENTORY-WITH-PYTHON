# ![image](https://user-images.githubusercontent.com/38144008/222943279-f69f3ae5-922e-42b8-9fe4-e080ef900354.png)

# CREATING A CSV FILE

In this section using la library `csv` we are generating the CSV file.

RUN CLI:    `/network_inventory.py nso_sandbox_testbed_same_credentials.yaml`

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
That is the final result we have a csv file with the devices. :)

![image](https://user-images.githubusercontent.com/38144008/222886340-be942370-1809-4ef4-8497-b5f329b45723.png)


```python
Assembling network inventory data from output.

network_inventory = [('core-rtr01', 'iosxr', '6.3.1', '3 days, 37 minutes', 'N/A'), ('core-rtr02', 'iosxr', '6.3.1', '3 days, 37 minutes', 'N/A'), ('dist-rtr01', 'iosxe', '17.3.2', '3 days, 36 minutes', '91EDY6XXOPI'), ('dist-rtr02', 'iosxe', '17.3.2', '3 days, 36 minutes', '9X9NDJ21PR5'), ('dist-sw01', 'nxos', '9.2(4)', '3 days, 0 hours,35 minutes', '9ORBHMVBPDB'), ('dist-sw02', 'nxos', '9.2(4)', '3 days, 0 hours,35 minutes', '9NLTHFK2289'), ('edge-firewall01', 'asa', '9.15(1)1', '3 days 0 hours', '9A3LTK7V6RD'), ('edge-sw01', 'ios', '15.2(20200924:215240)', '3 days, 30 minutes', 'N/A'), ('internet-rtr01', 'iosxe', '17.3.2', '3 days, 36 minutes', '9150TDM5N31')]

Writting inventory to file 2023-03-04-00-15-08_nso_sandbox_testbed_same_credentials_network_inventory.csv.
```
![image](https://user-images.githubusercontent.com/38144008/222886459-75569c63-3841-417d-aca3-c756d4a32554.png)


# REFERNCES

+ Creation from [Excel File](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file)
+ [Devnet Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) to test owner Inventory
+ [JSON](https://jsonlint.com/) to test format


+ Learning Labs - Cisco
https://learningnetwork.cisco.com/s/

# REFERNCES

* Download in your machine [Summer 2021 Devasc-Prep-Network-Inventory-01](https://github.com/hpreston/summer2021-devasc-prep-network-inventory-01.git) maked by Hank Preston, that is a guide if you need help to develop all the code related how to make an inventory.
+ Creation from [Excel File](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file)
+ [Devnet Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) to test owner Inventory
+ [JSON](https://jsonlint.com/) to test format	
