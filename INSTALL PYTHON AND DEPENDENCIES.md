# ![image](https://user-images.githubusercontent.com/38144008/222942819-10c80282-fc4a-435c-bbe0-5924ead5ca52.png)

# INSTALL PYTHON AND DEPENDENCIES

To install python in your development environment. you can follow these steps.

+ Download Python via console.

`[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ wget https://www.python.org/ftp/python/3.10.2/Python-3.10.2.tgz`

+ Extract the downloaded archive by running the following command:

`[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ tar -xvf Python-3.10.2.tgz`

Navigate to the extracted directory by running the following command:

```bash
[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ cd Python-3.10.2

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ ./configure --enable-optimizations
```

Build and install Python 3.10 using the following command:

```bash
[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ make

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ sudo make altinstall
```

# CREATE VENV PYTHON 3.10.2 WITH PyATS

Note: PyATS just available in environments over Linux.

```bash
[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ python3.10 -m venv inventory

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ cd inventory

[opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ source inventory/bin/activate

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ python --version
Python 3.10.2
```
In this environment the version of python is `Python 3.10.2` 
```python
(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip list

Package    Version
---------- -------
pip        21.2.4
setuptools 58.1.0
WARNING: You are using pip version 21.2.4; however, version 23.0.1 is available.
You should consider upgrading via the '/home/opc/DEVNET/00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON/inventory/bin/python3.10 -m pip install --upgrade pip' command.

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip install --upgrade pip

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip install "pyats[full]"

(inventory) [opc@jenkins-master 00_AUTOMATING_A_NETWORK_INVENTORY_WITH_PYTHON]$ pip freeze > requirements.txt
```

# INSTALL TELNET IN LINUX

```bash
[opc@jenkins-master ~]$ sudo dnf install telnet

========================================================================================================================
 Package                 Architecture            Version                           Repository                      Size
========================================================================================================================
Installing:
 telnet                  x86_64                  1:0.17-76.el8                     ol8_appstream                   72 k

Transaction Summary
========================================================================================================================
Install  1 Package

Total download size: 72 k
Installed size: 119 k
Is this ok [y/N]: y
Downloading Packages:
telnet-0.17-76.el8.x86_64.rpm                                                           885 kB/s |  72 kB     00:00
------------------------------------------------------------------------------------------------------------------------
Total                                                                                   833 kB/s |  72 kB     00:00
Running transaction check
Transaction check succeeded.
Running transaction test
Transaction test succeeded.
Running transaction
  Preparing        :                                                                                                1/1
  Installing       : telnet-1:0.17-76.el8.x86_64                                                                    1/1
  Running scriptlet: telnet-1:0.17-76.el8.x86_64                                                                    1/1
  Verifying        : telnet-1:0.17-76.el8.x86_64                                                                    1/1

Installed:
  telnet-1:0.17-76.el8.x86_64

Complete!
```

+ Testing telnet in your environment.

```bash
[opc@jenkins-master ~]$ telnet 8.8.8.8 53
Trying 8.8.8.8...
Connected to 8.8.8.8.
Escape character is '^]'.
```

# DOWNLOAD THE GUIDE TO MAKE THE INVENTORY FROM GITHUB OF HANK PRESTON

* Download in your machine [Summer 2021 Devasc-Prep-Network-Inventory-01](https://github.com/hpreston/summer2021-devasc-prep-network-inventory-01.git) maked by Hank Preston, that is a guide if you need help to develop all the code related how to make an inventory.

# REFERNCES

+ Creation from [Excel File](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file)
+ [Devnet Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) to test owner Inventory
+ [JSON](https://jsonlint.com/) to test format
