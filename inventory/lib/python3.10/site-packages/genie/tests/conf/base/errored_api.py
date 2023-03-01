# unicon
from unicon.core.errors import SubCommandFailure
bla

def clear_interface_counters(device, interface='gigabit2'):
    """DUMMY API for UT"""
    log.info(
        "Clearing counters on interface {interface}".format(
            interface=interface
        )
    )

    try:
        device.execute(
            "clear counters {interface}".format(interface=interface)
        )
    except SubCommandFailure as e:
        raise SubCommandFailure(
            "Could not clear counters on {interface}. Error:\n{error}".format(
                interface=interface, error=e
            )
        )
