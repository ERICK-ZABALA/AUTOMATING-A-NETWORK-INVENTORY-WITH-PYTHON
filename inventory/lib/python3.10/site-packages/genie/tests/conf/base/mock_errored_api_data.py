
class MockApiJson:

    api = {
        "my_interface_counters": {
            "iosxe": {
                "doc": " clear interface counters\n\n        Args:\n            device (`obj`): Device object\n            interface (`str`): Interface name\n\n        Returns:\n            None\n\n        Raises:\n            SubCommandFailure\n    ",
                "module_name": "errored_api",
                "package": "genie.tests.conf.base.errored_api",
                "uid": "clear_interface_counters",
                "url": "blabla"
            }
        }
    }


def data_loader():
    return MockApiJson.api
