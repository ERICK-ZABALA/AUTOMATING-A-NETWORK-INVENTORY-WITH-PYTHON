
# [![image]( https://user-images.githubusercontent.com/38144008/222942190-0b3464ca-a7e4-4ade-9a69-a6c674808467.png)](https://www.youtube.com/watch?v=OMyOkqTOWWc)
[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON) [![Run in Cisco Cloud IDE](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-runable-icon.svg)](https://developer.cisco.com/devenv/?id=devenv-vscode-base&GITHUB_SOURCE_REPO=https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON)
# AUTOMATING A NETWORK INVENTORY WITH PYTHON

Automating a network inventory with Python pyats involves using the pyATS framework to simplify and accelerate the process of collecting and organizing information about network devices. By leveraging the power of Python programming, network administrators can create customized scripts that automate the collection of device data, enabling them to quickly and accurately generate an inventory of all devices on their network.

+ Click to Dino to check the video!!! 

+ How can we talk to the devices?
+ What tool / language will we use?
+ How do we create the list of devices to work with?
+ How will we share our code for others to use?
+ How do we protect any “secrets” (username/password)

# METHOD CLI

* Library to interact: PyATS
* Parse: regex, pyATS
* Spreadsheet: Std CSV


|Topics|Description|Title|Notes|
|---|---|---|---|
| INSTALL PYTHON AND DEPENDENCIES | Install Python 3.10.2.  | [INSTALL PYTHON AND DEPENDENCIES](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/INSTALL%20PYTHON%20AND%20DEPENDENCIES.md) | In this first step you install your Python. |
| INSTALL ANYCONNECT VPN CLIENT | Install VPN Client via CLI  | [INSTALL ANYCONNECT VPN CLIENT](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/INSTALL%20ANYCONNECT%20VPN%20CLIENT.md) | In this second step you install your vpn anyconnect client. |
| INSTALL GIT | Install GIT via CLI | [INSTALL GIT](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/INSTALL%20GIT.md) | In this step you install git in your environment. |
| CREATE SPREADSHEET | Create Spreadsheet  | [CREATE SPREADSHEET](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/CREATE%20SPREADSHEET.md) | In this step you create an Spreadsheet. |
| TESTING CONNECTIVITY | Testing Connectivity  | [TESTING CONNECTIVITY](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/TESTING%20CONNECTIVITY.md) | In this step you are going to make a testing connectivity. |
| GATHERING INFORMATION | Gathering show version and show inventory over devices with Python  | [GATHERING INFORMATION](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/GATHERING%20INFORMATION.md) | In this step you are going to begin gathering information. |
| FORMATTING FOR INVENTORY REPORT | Provide a correct format to generate a inventory report in Python  | [FORMATTING FOR INVENTORY REPORT](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/FORMATTING%20FOR%20INVENTORY%20REPORT.md) | In this step you are going to begin gathering information. |
| CREATING A CSV FILE | Provide a CSV File as a report in Python  | [CREATING A CSV FILE](https://github.com/ERICK-ZABALA/AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON/blob/main/CREATING%20A%20CSV%20FILE.md) | In this step you are going to provide a report via Python. |

# REFERENCES

* Download in your machine [Summer 2021 Devasc-Prep-Network-Inventory-01](https://github.com/hpreston/summer2021-devasc-prep-network-inventory-01.git) maked by Hank Preston, that is a guide if you need help to develop all the code related how to make an inventory.
+ Creation from [Excel File](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file)
+ [Devnet Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) to test owner Inventory
+ [JSON](https://jsonlint.com/) to test format
