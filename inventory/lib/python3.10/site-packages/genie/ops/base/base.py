import re
import copy
import time
import pickle
import logging
import inspect
from enum import Enum
from collections import deque

from .maker import Maker
from ...utils.diff import Diff
from genie.base import Base as _genie_Base
from genie.ops.ops_schema import Ops_structure

log = logging.getLogger(__name__)


class Context(Enum):
    '''Available Context, management protocol for Genie'''

    cli = 'cli'
    yang = 'yang'
    xml = 'xml'
    rest = 'rest'


class Base(_genie_Base):
    """Base class for all genie.ops objects

    Base class for all objects of the genie.ops infrastructure.

    """

    def __init__(self, device, connections=None, attributes=None,
                 commands=None, **kwargs):
        self.callables = {}
        self.device = device
        self.context_manager = {}
        self.attributes = attributes
        self.commands = commands
        self.connections = connections
        self.ops_schema = {}
        classname = self.__class__.__name__.lower()
        if not classname == 'base' and classname in Ops_structure.ops_schema:
            self.ops_schema = Ops_structure.ops_schema[classname]

        # A few that we know need to be diff ignored already.
        # Device will be compared by itself later,
        # As it cannot be pickled
        self.diff_ignore = deque(['maker', 'callables', 'device', 'diff_ignore', 'ops_schema'])

        # Create Maker already for the object
        # Remove boiler plate code
        self.raw_data = kwargs.pop('raw_data', False)
        self.maker = Maker(parent=self, attributes=self.attributes,
                           commands=self.commands, raw_data=self.raw_data)

    def add_leaf(self, cmd, *args, **kwargs):
        '''Wrapper to call self.maker'''
        # Evaluate if needed yang or something else
        if cmd in self.context_manager:
            if isinstance(self.context_manager[cmd], list):
                value = self.context_manager[cmd][0].value
            else:
                value = self.context_manager[cmd].value

            # This should be refactor. Mapping is not needed in most
            # of the code anymore
            if value not in self.device.mapping:
                if not hasattr(self.device, value):
                    # Want it, but dont have a connection?
                    raise Exception("Missing connection of "
                                    "type '{ty}' in the device "
                                    "mapping "
                                    "'{map}'".format(ty=value,
                                                     map=self.device.mapping))
                else:
                    dev = getattr(self.device, value)
            else:
                dev = self.device.connectionmgr.connections[value]
            self.maker.add_leaf(device=dev, cmd=cmd, *args, **kwargs)
        # Cmd not in cm, So cli.
        # Verify if there is a cli for pool
        elif 'cli' in self.device.mapping:
            if hasattr(self.device, 'cli'):
                dev = self.device.cli
            else:
                # This is needed for pure ops, the other one is for harness
                dev = getattr(self.device, self.device.mapping['cli'])
            self.maker.add_leaf(device=dev, cmd=cmd, *args, **kwargs)
        else:
            # Check how many connections on the device
            if len(self.device.connectionmgr.connections) == 1:
                # Take that one
                dev = list(self.device.connectionmgr.connections.values())[0]
                self.maker.add_leaf(device=dev, cmd=cmd, *args, **kwargs)
            else:
                # Just pass the device
                self.maker.add_leaf(device=self.device, cmd=cmd, *args, **kwargs)

    def make(self, *args, **kwargs):
        '''Wrapper to call self.maker'''
        self.maker.make(*args, **kwargs)

    def dict_to_obj(self, *args, **kwargs):
        '''Wrapper to call self.dict_to_obj'''
        self.maker.dict_to_obj(*args, **kwargs)

    def learn(self, **kwargs):
        '''Learn the feature from the parsed output'''
        # Need to be implemented in the script
        raise NotImplementedError

    def _diff_ignore(self, temp, ignores):
        '''Removed Ignore keys and regex'd keys'''

        # Temp represents the object.__dict__
        # And ignore is a list giving the structure (or variable) we want to
        # ignore

        # Take a backup, as the algo removes the value we shouldnt care about.
        ignore_tmp = deque(ignores)
        temp_copy = copy.deepcopy(temp)
        for item in ignores:
            ignore_tmp.popleft()
            if item.startswith('('):
                # Regex; so many paths might be there!
                # Verify if its only a value, or a dict
                if isinstance(temp, dict):
                    # A dict, so keep going
                    for key in temp_copy.keys():
                        # See if it matches
                        val = re.match(item, key)
                        if val:
                            # Matches
                            if ignore_tmp:
                                self._diff_ignore(temp[key], ignore_tmp)
                            else:
                                # This mean this is the last value, so
                                # remove what is under
                                del temp[key]
                        else:
                            # Doesn't match, so go next key
                            continue
                else:
                    # if it is not a dict, it means it is a leaf
                    # You can only ignore a key of a dictionary
                    # Not a valud
                    raise Exception('{item} is not a key'
                                    .format(item=item))
            else:
                if item in temp_copy:
                    if ignore_tmp:
                        temp = temp[item]
                        temp_copy = temp_copy[item]
                    else:
                        del temp[item]
                else:
                    # Doesnt exists, so just get out to go to the next one
                    break

    def to_dict(self):
        '''Convert each object into dictionary, and remove the diff_ignore
        value'''

        # If no ignore, just return __dict__
        if not self.diff_ignore:
            return self.__dict__

        # Taking a copy, as we will modify values, and it might modify the
        # self.__dict__ dict
        self_dict = {key: value for key, value in self.__dict__.items()
                                if key not in self.diff_ignore}
        copied = copy.deepcopy(self_dict)

        # Deal with the ignore keys now
        for ignore in self.diff_ignore:

            # Convert the string into a list, but we do not want to
            # affect the regular expression, so do some manipulation
            reg = re.findall('\(.*?\)', ignore)

            # Remove it from src and keep track of the position
            if reg:
                reg_src = {}
                for reg_item in reg:
                    reg_src[ignore.find(reg_item)] = reg_item
                    ignore = ignore.replace(reg_item, ' ' * len(reg_item), 1)

            # Create a space where the string dict is
            ignore = ignore.replace('[', ' ').replace(']', ' ')

            # Now put the regex back
            if reg:
                for key, value in reg_src.items():
                    ignore = ignore[:key] + value + ignore[key+len(value):]

            # And create the list
            ignore = ignore.split()

            self._diff_ignore(copied, ignore)

        return copied

    def __eq__(self, other):
        '''Compare __dict__, but remove the diff_ignore attributes/keys'''

        try:
            assert isinstance(self, Base) and isinstance(other, Base)
        except AssertionError:
            return False

        # As device cannot be deepcopied
        if self.device is not other.device:
            return False

        self_dict = self.to_dict()
        other_dict = other.to_dict()

        return self_dict == other_dict

    def diff(self, post, exclude=None):
        '''Fancier compare, which returns a str of what has been compared'''
        assert isinstance(self, Base) and isinstance(post, Base)

        if not exclude:
            exclude = []

        pre_dict = self.to_dict()
        post_dict = post.to_dict()

        diff = Diff(post_dict, pre_dict, exclude=exclude)
        diff.findDiff()
        return diff

    def learn_poll(self, sleep=None, attempt=None, timeout=None,
                   verify=None, ops_keys=None, **kwargs):
        # Either sleep + attempt, or timeout Object
        if timeout and not sleep and not attempt:
            return self._learn_poll_timeout(timeout, verify, ops_keys, **kwargs)

        # Make sure sleep and attempt
        if not sleep and not attempt:
            raise TypeError("learn_poll() missing required arguments: "\
                            "'sleep' and 'attempt'")
        if not attempt:
            raise TypeError("learn_poll() missing required arguments: "\
                            "'attempt'")

        ret = None
        for count in range(attempt):
            log.info('Attempt #{} to learn {} for {}'.format(count+1,
                                                             repr(self),
                                                             self.device.name))
            ret = self._poll(verify, ops_keys, **kwargs)
            if ret is None:
                return

            # Reset all the leafs
            time.sleep(sleep)

        raise StopIteration('Maximum amount of retries to '
                            'learn {r}'.format(r=repr(self))) from ret

    def _learn_poll_timeout(self, timeout, verify, ops_keys, **kwargs):
        ret = None
        while timeout.iterate():
            ret = self._poll(verify, ops_keys, **kwargs)
            if ret is None:
                return
            timeout.sleep()

        raise StopIteration('Maximum amount of retries to '
                            'learn {r}'.format(r=repr(self))) from ret

    def _poll(self, verify, ops_keys, **kwargs):
        exception = None
        try:
            if not ops_keys:
                ops_kwargs = {}
            else:
                # check what args ops takes, pass only the keys self.learn() accepts
                args = inspect.getfullargspec(self.learn).args
                ops_kwargs = {}
                for key in ops_keys:
                    if key in args:
                        ops_kwargs[key] = ops_keys[key]
            self.learn(**ops_kwargs)
            if verify:
                try:
                    # Learn passed
                    verify(self, **kwargs)
                    return
                except Exception as e:
                    # Verify log
                    log.debug(e)
                    exception = e
            else:
                return
        except Exception as e:
            # Learn failed
            log.debug(e)
            exception = e

        # Reset all the leafs
        self.maker._reset()
        return exception

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()

        # Remove the unpicklable entries.
        try:
            state['device'] = state['device'].name
        except (KeyError, AttributeError):
            pass

        try:
            del state['maker']
        except KeyError:
            pass

        # Commented out for testing. Uncomment before release.
        # self.diff_ignore = deque(['maker', 'callables', 'device', 'diff_ignore', 'ops_schema'])

        return state

    def unpickle(self, value):
        '''Unpickle the ops object'''
        if not value:
            return

        obj = pickle.loads(value)

        return obj

    def pickle(self, obj_to_pickle):
        '''Pickle ops object'''

        if not obj_to_pickle:
            return

        # pickle object into a string
        string_name = pickle.dumps(obj_to_pickle)

        return string_name
