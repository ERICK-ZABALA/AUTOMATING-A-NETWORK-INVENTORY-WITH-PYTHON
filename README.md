
# AUTOMATING A NETWORK INVENTORY WITH PYTHON

+ how can we talk to the devices?
+ what tool / language will we use?
+ How do we create the list of devices to work with?
+ How will we share our code for others to use?
+ How do we protect any “secrets” (username/password)

# CLI METHOD

Library to interact: Netmiko, Nornir, NAPALM, Scrapli, PyATS, Ansible, others
Parse: str.find, regex, TextFSM, pyATS, others
Spreadsheet: STD CSV

# CREATE VENV PYTHON 3.10.2 WITH PyATS

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ python3.10 -m venv inventory

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ source inventory/bin/activate

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ python --version

Python 3.10.2
(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip list
Package    Version
---------- -------
pip        21.2.4
setuptools 58.1.0
WARNING: You are using pip version 21.2.4; however, version 23.0.1 is available.
You should consider upgrading via the '/home/opc/DEVNET/00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON/inventory/bin/python3.10 -m pip install --upgrade pip' command.

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip install --upgrade pip

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip install pyats[all]

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip freeze > requirements.txt





