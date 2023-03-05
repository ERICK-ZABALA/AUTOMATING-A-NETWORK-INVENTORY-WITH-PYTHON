
# AUTOMATING A NETWORK INVENTORY WITH PYTHON

+ how can we talk to the devices?
+ what tool / language will we use?
+ How do we create the list of devices to work with?
+ How will we share our code for others to use?
+ How do we protect any “secrets” (username/password)

# SOLUTION FINAL - VIDEO

![image](https://user-images.githubusercontent.com/38144008/222942136-58efce94-54c8-47ca-8e83-c0d90d9b2122.png)


![image](https://user-images.githubusercontent.com/38144008/222941593-cb3236e3-5555-40d3-a503-8e66fb56600c.png)




# METHOD CLI

* Library to interact: Netmiko, Nornir, NAPALM, Scrapli, PyATS, Ansible, others
* Parse: str.find, regex, TextFSM, pyATS, others
* Spreadsheet: STD CSV


|Feature|Description|Title|Notes|
|---|---|---|---|
| INSTALL PYTHON AND DEPENDENCIES | Install Python 3.10.2.  | [INSTALL PYTHON AND DEPENDENCIES](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/INSTALL%20PYTHON%20AND%20DEPENDENCIES.md) | In this first step you install your Python. |
| INSTALL ANYCONNECT VPN CLIENT | Install VPN Client via CLI  | [INSTALL ANYCONNECT VPN CLIENT](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/INSTALL%20ANYCONNECT%20VPN%20CLIENT.md) | In this second step you install your vpn anyconnect client. |
| INSTALL GIT | Install GIT via CLI | [INSTALL GIT](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/INSTALL%20GIT.md) | In this step you install git in your environment. |
| CREATE SPREADSHEET | Create Spreadsheet  | [CREATE SPREADSHEET](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/CREATE%20SPREADSHEET.md) | In this step you create an Spreadsheet. |
| TESTING CONNECTIVITY | Testing Connectivity  | [TESTING CONNECTIVITY](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/TESTING%20CONNECTIVITY.md) | In this step you are going to make a testing connectivity. |
| GATHERING INFORMATION | Gathering show version and show inventory over devices with Python  | [GATHERING INFORMATION](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/GATHERING%20INFORMATION.md) | In this step you are going to begin gathering information. |
| FORMATTING FOR INVENTORY REPORT | Provide a correct format to generate a inventory report in Python  | [FORMATTING FOR INVENTORY REPORT](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/FORMATTING%20FOR%20INVENTORY%20REPORT) | In this step you are going to begin gathering information. |
| CREATING A CSV FILE | Provide a CSV File as a report in Python  | [CREATING A CSV FILE](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/CREATING%20A%20CSV%20FILE.md) | In this step you are going to provide a report via Python. |

# REFERNCES

+ Creation from [Excel File](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file)
+ [Devnet Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) to test owner Inventory
+ [JSON](https://jsonlint.com/) to test format
