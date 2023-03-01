import inspect
import logging
import collections

logger = logging.getLogger(__name__)

def default_builder(tokens, *, mandatory = ()):
    '''default_builder

    A token sequence builder takes in a mandatory list of 'tokens' as specified
    by the user, and any other keyword arguments necessary, and returns the 
    abstraction lookup sequence by combining the tokens into appropriate lookup
    combinations.

    This default builder is a blend between usability and complexity, allowing
    for token dependencies and mandatory tokens. 

    Arguments
    ---------
        tokens (list): list of string tokens specified by the user, propagated
                       down from Lookup() class.
        mandatory (iterable): list/tuple of tokens that are mandatory, eg,
                              they must appear in the lookup sequence.

    Returns
    -------
        list of tuples

    Example
    -------
        >>> default_builder(['os', 'series', 'type', 'yang', 'release'],
                            mandatory =['yang'])
        [('os', 'series', 'type', 'yang', 'release'), 
         ('os', 'series', 'type', 'yang'),
         ('os', 'series', 'yang'), 
         ('os', 'yang'), 
         ('yang',)]
    '''

    # check mandatory tokens are part of tokens list
    if not set(mandatory).issubset(tokens):
        raise ValueError('mandatory tokens must be part of the overall tokens '
                         'list. Extras: %s' % (set(mandatory) - set(tokens)))

    # start with the full set of tokens
    combinations = []

    # loop through token positions in reverse order
    # (token reduction mechanism)
    for position in range(len(tokens), -1, -1):

        # create a new combination
        # (keep mandatory tokens in place)
        # (must be a tuple)
        combo = tuple(token for pos, token in enumerate(tokens) 
                               if pos < position or token in mandatory)

        # avoid duplications
        # (the above logic generate duplicates)
        if combo not in combinations:
            combinations.append(combo)

    # return all combinations
    return combinations

def get_caller_stack_pkgs(stacklvl = 1):
    '''get_caller_stack_pkgs

    helper function, returns a dictionary of names/abstraction module based on 
    the caller's stack frame. 

    Example
    -------
        >>> import genie
        >>> import mylib as local_lib
        >>> get_caller_stack_pkgs()
        {'genie': <module genie...>,
         'local_lib': <module mylib...>,}
    '''

    # get the caller FrameInfo
    # (frame, filename, lineno, function, code_context, index) 
    frame = inspect.stack()[stacklvl][0]

    # variable scope = locals + globals
    f_scope = collections.ChainMap(frame.f_locals, frame.f_globals)

    # look for imported abstract packages
    return {n: o for n, o in f_scope.items() if hasattr(o, '__abstract_pkg')}


# global setting for default builder
DEFAULT_BUILDER = default_builder


class Lookup(object):
    '''Lookup

    When instanciated with a set of "token requirements", the lookup object 
    allows users to dynamically reference libraries (abstraction packages).
    
    The concept is akin to dynamic imports. As opposed to 

        >>> from genie.nxos import Ospf
        >>> from local_lib.nxos.titanium import Blah

    lookup allows the user to simply do:

        >>> import genie
        >>> import local_lib
        >>> l = Lookup('nxos', 'titanium')
        >>> l.Ospf()
        >>> l.Blah()

    where the actual import based on the given tokens will be sorted out for
    the user dynamically.

    Arguments
    ---------
        *tokens (list of str): list of tokens specified for this lookup object
        builder (func): function used for creating the lookup token sequence
        packages (dict): dictionary of package names and their module object.
                         if not provided, the caller's stack is looked up for
                         all available abstraction packages.
        **builder_kwargs (kwargs): any other keyword arguments for the 
                                   sequence builder.
    
    Examples
    --------
        >>> import my_abstracted_lib as lib
        >>> l = Lookup('nxos', 'titanium')
        >>> l.lib.module_a.module_b.MyClass()
    '''

    def __init__(self, 
                 *tokens, 
                 builder = None, 
                 packages = None, 
                 **builder_kwargs):

        # tokens for lookup
        self._tokens = tokens

        # lookup order builder and its kwargs
        self._builder = builder or DEFAULT_BUILDER
        self._builder_kwargs = builder_kwargs

        # packages available for lookup
        # (default to collecting from caller stack)
        packages = packages or get_caller_stack_pkgs(stacklvl = 2)

        # build database
        self._pkgs = {}

        for name, module in packages.items():
            # get the abstraction package object
            # use getattr() and avoid name mangling
            self._pkgs[name] = getattr(module, '__abstract_pkg')

            # make sure package is learnt
            self._pkgs[name].learn()

        # build lookup order
        self._sequence = self._builder(tokens, **builder_kwargs)

    def __dir__(self):
        '''__dir__

        built-in, returns the packages available for calling
        '''
        return super().__dir__() + list(self._pkgs.keys())

    def __getattr__(self, pkg):
        '''__getattr__

        black magic. Wraps abstraction packages with AbstractionModule - a 
        dynamic search mechanism that tracks the user attribute getter path
        and returns the most complete/corresponding object.
        '''
        try:
            pkg = self._pkgs[pkg]
        except KeyError:
            raise AttributeError("'%s' is not a recognized abstract package. "
                                 "Import it first before creating %s object." 
                                 % (pkg, self.__class__.__name__))

        # AbstractedModule will chain the objects together
        # (each getattr at this level gets a new instance)
        return AbstractedModule(package = pkg, sequence = self._sequence)

    @classmethod
    def tokens_from_device(cls,
                           device,
                           default_tokens = None,
                           **kwargs):
        abstraction_info = {}

        try:
            abstraction_info = device.custom['abstraction']
            # get the abstraction key order
            token_order = abstraction_info['order']

        except (KeyError, AttributeError):
            if default_tokens:
                token_order = default_tokens
            else:
                raise ValueError('Expected device to have custom.abstraction '
                                 'definition, or provide default tokens to '
                                 'use in Lookup.from_device() call') from None

        # build tokens
        tokens = []
        for token in token_order:
            if abstraction_info and token in abstraction_info:
                tokens.append(abstraction_info[token])
            elif hasattr(device, token):
                tokens.append(getattr(device, token))
            elif 'order' in abstraction_info:
                # information came from abstraction-info are mandatory
                raise ValueError('Could not find value for token {token} under '
                                 'device.custom.abstraction.{token} nor device'
                                 '.{token}'.format(token = token))
        return tokens

    @classmethod
    def from_device(cls,
                    device,
                    packages = None,
                    default_tokens = None,
                    **kwargs):
        '''from_device

        creates an abstraction Lookup object by getting the token arguments from
        a pyATS device objects.

        This api expects the device object to have an "abstraction" dictionary
        under 'custom' attribute. Eg:

        Example
        -------
            devices:
                my-device:
                    custom:
                        abstraction:
                            order: [os, serie, context]
                            os: nxos
                            serie: n7k
                            context: yang

        Arguments
        ---------
            device (Device): pyATS topology device object
            builder (func): function used for creating the lookup token sequence
            packages (dict): dictionary of package names and their module object.
                             if not provided, the caller's stack is looked up
                             for all available abstraction packages.
            default_tokens (list): list of default tokens specified to lookup 
                                   from device.
            **builder_kwargs (kwargs): any other keyword arguments for the 
                                       sequence builder.
        '''

        tokens = cls.tokens_from_device(device, default_tokens=default_tokens)

        # lookup packages..
        packages = packages or get_caller_stack_pkgs(stacklvl = 2)

        # create lookup object
        return cls(*tokens, packages = packages, **kwargs)


class AbstractedModule(object):
    '''AbstractedModule

    Internal class, part-two of lookup mechanism. This class is instanciated
    each time a successful package reference (through Lookup class instances)
    is done, and tracks internally user's attribute chain, used as part of the
    lookup process.

    Arguments
    ---------
        package (AbstractPackage): the abstract package to reference
        sequence (list): sequence of tokens to perform lookup.

    '''

    def __init__(self, package, sequence):
        self._package = package
        self._sequence = sequence

        # relative path taken for this lookup: Lookup().lib.x.y.z
        # (always starts with the package name)
        self._path = tuple(package.name.split('.'))

    def __getattr__(self, name):
        '''__getattr__

        getattr() magic. This is where the user's attribute lookup chain is
        stored & reflected. Eg, when user look sup a.b.c.d, the referring module
        is a.b.c and the object to lookup is d.

        Logic:
            - build path around user's getattr() calls.
            - check whether the given path is a known on in this abstraction
              package
            - if it is, keep building the path.
            - else, we've hit a dead end, try to collect the object from the 
              last-known module. 
            - if found, return it
            - else - search unknown, raise exception.
        '''

        # build the new path from name
        path = self._path + (name, )

        # is this path still part of this package?
        if path in self._package:
            # still within the realm of this package
            self._path = path
            return self

        # no longer within a known path
        # start abstracting for a result
        # (follow given sequece)
        for seq in self._sequence:
            try:
                # return what we find
                return self._package.lookup(self._path, seq, name)

            except LookupError:
                # ignore errors for now
                pass

        # found nothing... raise exception to the user
        raise LookupError("No such attribute in abstraction package '%s': '%s'" 
                            %  (self._package.name, '.'.join(path)))

    def __repr__(self):
        return "<%s '%s' from '%s'>" % (self.__class__.__name__, 
                                            '.'.join(self._path), 
                                            self.__file__)

    def __dir__(self):
        # include the current known path's dir() result
        return super().__dir__() + self.__getattr__('__dir__')()
