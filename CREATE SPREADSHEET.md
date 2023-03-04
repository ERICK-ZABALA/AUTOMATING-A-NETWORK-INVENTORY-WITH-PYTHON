
# CREATE SPREADSHEET

* We are going to create owner `Spreedsheet` [Sample Test Bed File](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html#creation-from-excel-file)

PyATS work over YAML consider this point. PyATS uses a testbed.yaml to make an inventory.
We are going to create owner list of devices using this [template](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/_downloads/b05328b78497f390ee873500df1aaa94/SampleTestbedFile.xlsx).

In this template we are going to collect all the devices.

![image](https://user-images.githubusercontent.com/38144008/222002305-9587f85a-bf1e-4aa4-835c-0a2c9d3384d1.png)

We are going to [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology
). You need an account of cisco to register this sandbox is [free!!!](https://id.cisco.com/signin/register).

![image](https://user-images.githubusercontent.com/38144008/222004497-c3c37576-83cb-4067-927b-ad4704e62d0d.png)

![image](https://user-images.githubusercontent.com/38144008/222009619-eea78d14-3f55-4d08-86e4-5b2a424a3a3c.png)

![image](https://user-images.githubusercontent.com/38144008/222930335-ec242a99-c97d-4c11-9178-350c34193a4d.png)

We are going to register all the devices Cisco in owner file like this:

![image](https://user-images.githubusercontent.com/38144008/222009578-254b6427-95a1-451f-b516-d8b379188bf6.png)

`Username` is requeried to work with the tool and put in blank the section password to `%ASK{}`.

```bash
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  README.md  sample
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ pyats create testbed file --path sample/nso_sandbox_devices.xlsx --output nso_sandbox_testbed.yaml -v
Testbed file generated: 
sample/nso_sandbox_devices.xlsx -> nso_sandbox_testbed.yaml
```
You should see the next file nso_sandbox_testbed.yaml in your virtual environment.

```yaml
devices:
  core-rtr01:
    connections:
      cli:
        ip: 10.10.20.173
        protocol: telnet
    credentials:
      default:
        password: '%ASK{}'
        username: cisco
      enable:
        password: '%ASK{}'
    os: iosxr
    platform: core-rtr01
    type: iosxr ...
```

# IMPROVING US TESTBED FILE

In this section we are going to improve our code alocated the credentials to begin. In this scenario we are working with the same credentials for all devices.

```yaml
testbed:
  credentials:
    default:
      password: '%ASK{}'
      username: '%ASK{}'
    enable:
      password: '%ASK{}'
```

Running: nso_sandbox_testbed_same_credentials.yaml

```bash
inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  nso_sandbox_testbed.yaml  README.md  sample
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ pyats validate testbed --testbed nso_sandbox_testbed_same_credentials.yaml
Loading testbed file: nso_sandbox_testbed_same_credentials.yaml
--------------------------------------------------------------------------------
Enter default password for testbed: cisco

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: cisco

Testbed Name:
    nso_sandbox_testbed_same_credentials

Testbed Devices:
.
|-- core-rtr01 [iosxr/core-rtr01]
|-- core-rtr02 [iosxr/core-rtr02]
|-- dist-rtr01 [iosxe/dist-rtr01]
|-- dist-rtr02 [iosxe/dist-rtr02]
|-- dist-sw01 [nxos/dist-sw01]
|-- dist-sw02 [nxos/dist-sw02]
|-- edge-firewall01 [asa/edge-firewall01]
|-- edge-sw01 [ios/edge-sw01]
-- internet-rtr01 [iosxe/internet-rtr01]
`
YAML Lint Messages
------------------
  4:81      warning  line too long (113 > 80 characters)  (line-length)
  5:81      warning  line too long (81 > 80 characters)  (line-length)
  6:81      warning  line too long (86 > 80 characters)  (line-length)

Warning Messages
----------------
 - Device 'core-rtr01' has no interface definitions
 - Device 'core-rtr02' has no interface definitions
 - Device 'dist-rtr01' has no interface definitions
 - Device 'dist-rtr02' has no interface definitions
 - Device 'dist-sw01' has no interface definitions
 - Device 'dist-sw02' has no interface definitions
 - Device 'edge-firewall01' has no interface definitions
 - Device 'edge-sw01' has no interface definitions
 - Device 'internet-rtr01' has no interface definitions
`
(inventory) [opc@jenkins-master AUTOMATING-A-NETWORK-INVENTORY-WITH-PYTHON]$ ls
inventory  `nso_sandbox_testbed_same_credentials.yaml`  nso_sandbox_testbed.yaml  README.md  sample
```
