

from unicon.eal.dialogs import Dialog

class BaseState():
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
        if isinstance(self.pattern, list) or isinstance(self.pattern, tuple):
            # all list elements must be string
            for pattern in self.pattern:
                if not isinstance(pattern, str):
                    raise Exception('pattern must be string')
        else:
            # it is not list or tuple, hence it must be string
            if not isinstance(self.pattern, str):
                raise Exception('pattern must be str, list or tuple')

    def validate_transitions(self):

        if not isinstance(self.transitions, (list, tuple)):
            raise Exception('Transition should a list of state,exec' +
                            'or a list of list')
        else:
            for state,path in self.transitions:

                if isinstance(state, BaseState) or isinstance(state, str):
                    raise Exception('Invalid state')
                if callable(path):
                    raise Exception('Path should be callable')

    def validate_prompt(self):

        if not isinstance(self.prompt, Dialog):
            return Dialog(self.prompt)
        else:
            return self.prompt

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

        return self.states

if __name__ == '__main__':
    pass

