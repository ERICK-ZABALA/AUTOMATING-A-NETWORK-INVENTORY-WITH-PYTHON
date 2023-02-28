from unicon.trial.states import StateTableInfo
from unicon.trial.states import State

class DeviceTypeMeta(type):

    device_types = {}

    def __new__(cls, *args, **kwargs):

        class_name = args[0]

        if class_name in cls.device_types:
            return cls.device_types[class_name]

        classobj = super().__new__(cls, *args, **kwargs)
        classobj.state_table = StateTableInfo()

        return classobj

class GenericDeviceType(metaclass=DeviceTypeMeta):

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def add_state(cls, state):

        cls.state_table.add_state(state)
        pass

    @classmethod
    def get_state(cls):

        states_available = {}
        base_clases = cls.mro()

        for _class in base_clases[::-1]:
            if not _class == object:
                states = _class.state_table.get_state()
                states_available.update(states)

        return states_available

    @staticmethod
    def walk_through_states(states_available, from_state, to_state):

        if to_state in states_available[from_state].transitions.keys():
            return [to_state]

        for trans_state in states_available[from_state].transitions.keys():
            ret_state = GenericDeviceType.walk_through_states(states_available, trans_state, to_state)

            if ret_state is not None:
                trans_state = [trans_state]
                trans_state.extend(ret_state)
                return trans_state
        return None

    @classmethod
    def get_transition_path(cls, from_state, to_state):

        states_available = cls.get_state()

        if from_state not in states_available:
            raise Exception('Unkown source State' + str(from_state))
        if from_state not in states_available:
            raise Exception('Unkown source State' + str(to_state))

        path = GenericDeviceType.walk_through_states(states_available, from_state, to_state)
        return path

class RouterType(GenericDeviceType):
    pass

if __name__ == '__main__':

    from unicon.eal.helpers import *
    from unicon.eal.dialogs import Dialog, Statement

    hostname = r'^.*si-tvt-7200-28-42'
    enable_prompt = hostname + r'#$'
    disable_prompt = hostname + r'>$'
    config_prompt = hostname + r'(config)#$'

    connect_statements = [

        Statement(r"^.*Escape character is '\^\]'\.", action=None, loop_continue=True),
        Statement(r'^.*Username:\s?',
                  action=sendline, args={'command': 'lab'},
                  loop_continue=True),

        Statement(r'^.*Password: $',
                  action=sendline, args={'command': 'lab'},
                  loop_continue=True),

    ]
    dia = Dialog(connect_statements)

    enable_state = State(name='enable',
                         patterns=enable_prompt,
                         prompts=dia,
                         transitions={'disable': 'disable', 'config': 'config terminal', 'linux': 'attach linux'})

    disable_state = State(name='disable',
                          patterns=disable_prompt,
                          prompts=dia,
                          transitions={'enable': 'enable'})

    config_state = State(name='config',
                         patterns=config_prompt,
                         prompts=dia,
                         transitions={'enable': 'end'})

    linux_state = State(name='linux',
                        patterns=r'linux.*#',
                        prompts=dia,
                        transitions={'enable': 'exit'})
    n7k_linux_state = State(name='linux',
                            patterns=r'linux.*#',
                            prompts=dia,
                            transitions={'enable': 'exit'})


    class NxosType(RouterType):
        pass

    class N7kType(NxosType):
        states = []
        pass


    NxosType().add_state(linux_state)
    N7kType().add_state(n7k_linux_state)
    RouterType().add_state(enable_state)
    RouterType().add_state(disable_state)
    RouterType().add_state(config_state)
    states = N7kType.get_state()
    N7kType.get_transition_path('config','disable')
