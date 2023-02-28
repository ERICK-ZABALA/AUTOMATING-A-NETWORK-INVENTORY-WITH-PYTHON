from unicon.eal.dialogs import Dialog, Statement


class BaseStateMeta(type):
    def __new__(cls, *args, **kwargs):
        classobj = super().__new__(cls, *args, **kwargs)
        return classobj

class BaseState(metaclass=BaseStateMeta):

    def __init__(self, name, patterns, prompts, transitions):
        self.name = name
        self.patterns = patterns
        self.validate_pattern()

        self.prompts = prompts
        self.prompts = self.validate_prompt()
        self.transitions = transitions
        self.validate_transitions()

    def validate_pattern(self):
        """ validate the pattern part of the statement """
        if isinstance(self.patterns, list) or isinstance(self.patterns, tuple):
            # all list elements must be string
            for pattern in self.patterns:
                if not isinstance(pattern, str):
                    raise Exception('pattern must be string')
        else:
            # it is not list or tuple, hence it must be string
            if not isinstance(self.patterns, str):
                raise Exception('pattern must be str, list or tuple')

    def validate_transitions(self):

        if not isinstance(self.transitions, dict):
            raise Exception('Transition should a list of state,exec' +
                            'or a list of list')
        else:
            for state,path in self.transitions.items():

                if not isinstance(state, str):
                    raise Exception('Invalid state', state)
                if not isinstance(path, str):
                    raise Exception('Path should be valid device command')

    def validate_prompt(self):

        if not isinstance(self.prompts, Dialog):
            return Dialog(self.prompts)
        else:
            return self.prompts

    def __str__(self):
        return self.name

class State(BaseState):
    pass

class StateTableInfo(object):

    def __init__(self):

        self.states = []

    def add_state(self, state):
        if not isinstance(state, BaseState):
            raise Exception('Invalid State')

        self.states.append(state.name)
        setattr(self, state.name, state)

    def get_state(self):

        state_dict = {}
        for state_name in self.states:

            state_dict[state_name] = getattr(self,state_name)

        return state_dict


if __name__ == '__main__':

    from unicon.eal.helpers import *

    hostname = r'^.*si-tvt-7200-28-42#$'
    connect_statements = [

        Statement(r"^.*Escape character is '\^\]'\.", action=None, loop_continue=True),
        Statement(r'^.*Username:\s?',
                  action=sendline, args={'command': 'lab'},
                  loop_continue=True),

        Statement(r'^.*Password: $',
                  action=sendline, args={'command': 'lab'},
                  loop_continue=True),
    ]
    exec_dia = Dialog(connect_statements)

    s1 = State(name='enable',
            patterns=hostname,
            prompts=exec_dia,
            transitions={'disable': 'enable', 'config': 'end'})
    print(s1)

    s2 = State(name='disable',
            patterns=hostname,
            prompts=exec_dia,
            transitions={'enable': 'disable'})
    print(s2)

    s3 = State(name='config',
            patterns=hostname,
            prompts=exec_dia,
            transitions={'enable': 'config terminal'})
    print(s3)
