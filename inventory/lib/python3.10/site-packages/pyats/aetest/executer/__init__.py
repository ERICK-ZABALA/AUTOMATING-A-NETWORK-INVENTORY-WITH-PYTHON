import sys
import inspect

from .implementation import Executer

class ExecuterRedirect(object):

    # declare module as infra
    # note - declaring here because module = obj
    __aetest_infra__ = True

    def __init__(self):
        # create default executer
        self.__executer__ = Executer()

    def __getattr__(self, attr):
        '''Built-in __getattr__ function

        Called when getattr() this object and the object doesn't exist. Used
        to redirect calls to the actual __executer__ object

        '''

        return getattr(self.__executer__, attr)

    def change_to(self, executer):
        self.__executer__ = executer

    def __setattr__(self, name, value):
        '''Built-in __setattr__ function

        This function redirects setting executer attributes to the encapsulated
        __executer__ instance (the actual executor object).

        Because this object is an ultimate redirect to the actual executer 
        instance, all of its own internal variables should begin with _ or __ to
        avoid name clashing.
        '''

        if name.startswith('_'):
            # any attributes with _ or __ is internal to me
            return super().__setattr__(name, value)
        else:
            # everything else belongs to executer object instance
            return setattr(self.__executer__, name, value)


extras = inspect.getmembers(sys.modules[__name__], callable)

sys.modules[__name__] = redirector = ExecuterRedirect()

for name, value in extras:
    setattr(redirector, name, value)

# hardwire all module hidden attributes to redirector instance
redirector.__file__    = __file__
redirector.__loader__  = __loader__
redirector.__package__ = __package__
redirector.__name__    = __name__
redirector.__path__    = __path__
redirector.__spec__    = __spec__
redirector.__doc__     = __doc__
