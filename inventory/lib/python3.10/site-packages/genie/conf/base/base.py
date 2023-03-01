import os
import collections
from collections import abc
import logging
import inspect
import weakref

from genie.abstract import lookup
from pyats import configuration as cfg
from pyats.utils.objects import find, R
from pyats.datastructures import WeakList
from pkg_resources import iter_entry_points


from genie.base import Base as _genie_Base
from .decorator import log_it
from .exceptions import CountError

log = logging.getLogger(__name__)

PYATS_EXT_CONF = 'pyats.libs.external.conf'
CONF_ENTRYPOINT = 'genie.libs.conf'


class Base(_genie_Base):
    """Base class for all genie.conf objects

    Base class for all objects of the genie.conf infrastructure.
    All of these objects are related to a Testbed.

    `__init__` allows to set all `**kwargs` to be set automatically
    in the object.

    Notes:

        Derived classes that implement equality (__eq__) operations must
        consider the `testbed` objects belong to.  This consideration if very
        important because the `Base` class keeps lists of instances and
        otherwise-equivalent objects must be considered unequal if they belong
        to different testbeds or some instances may become unreacheable
        missing.
    """

    __instances = collections.defaultdict(weakref.WeakSet)

    @classmethod
    def _Base_instances(cls, testbed=None, subclasses=True):
        instances = Base.__instances.get(cls, ())
        if testbed:
            instances = [instance
                         for instance in instances
                         if getattr(instance, 'testbed', None) is testbed]
        if subclasses:
            instances = set(instances).union(
                *[subcls._Base_instances(testbed=testbed)
                  for subcls in cls.__subclasses__()])
        return frozenset(instances)

    def __new__(cls, *args, **kwargs):
        from genie.harness.utils import load_attribute

        device = kwargs.get('device', None)
        relative_module_name = cls.__module__.replace(f"{CONF_ENTRYPOINT}.", '')
        relative_class_name = f"{relative_module_name}.{cls.__qualname__}"
        pkgs = []

        # Check external/local Conf package
        ext_conf_package = cfg.get(PYATS_EXT_CONF, None) or \
            os.environ.get(PYATS_EXT_CONF.upper().replace('.', '_'))
        if ext_conf_package:
            pkgs.append(ext_conf_package)

        # Check Conf entrypoints
        for entry in iter_entry_points(group=CONF_ENTRYPOINT):
            pkgs.append(entry.module_name)

        for pkg in pkgs:
            try:
                new_class = load_attribute(pkg, relative_class_name, device, suppress_warnings=True)
            except ValueError:
                # ValueError occurs if device is not yet defined
                continue
            else:
                if cls.__name__ == new_class.__name__:
                    log.debug(
                        f"Default genie.libs.conf class for '{relative_class_name}' "
                        f"superseded. Using class from '{pkg}' instead")
                    return super().__new__(new_class)

        return super().__new__(cls)

    def __init__(self, **kwargs):

        # For each kwargs, set it to its value
        for key, value in kwargs.items():
            setattr(self, key, value)

        try:
            testbed = self.testbed
        except AttributeError as e:
            from genie.conf import Genie
            if not Genie.testbed:
                raise TypeError(
                    '%s object cannot be instantiated without a testbed' % (
                        self.__class__.__name__,)) from e
            self.testbed = Genie.testbed

        super().__init__(**kwargs)

        # Tracking of Base.__instances into a WeakSet can't be done in
        # __new__ because it is likely that some hash keys are not yet set.
        cls = self.__class__
        if issubclass(cls, abc.Hashable):
            Base.__instances[cls].add(self)

    def _find_objects(self, *rs, iterable=None, count=None, cls=None,
                      **kwargs):
        """Base function for find_<object>

        Please refer to the actual implementation on how to use it.
        Part of Testbed, Device and Links.
        """
        assert iterable is not None

        # Make sure count is positive
        if count is not None and count < 0:
            raise TypeError('count can only be a positive number. {c} '
                            'is not positive.'.format(c=count))
        if cls is None:
            raise TypeError('cls must be provided')

        if not rs:
            rs = rs = [R(**kwargs)]
            kwargs = {}
        elif kwargs:
            # Merge kwargs with all the existing R
            new_kwargs = {}
            for r in rs:
                for k in kwargs:
                    if k not in r.kwargs:
                        r.kwargs[k] = kwargs[k]
                        continue
                    log.warning('{k} already in the requirements '
                                'of {r}'.format(k=k, r=r))
                    new_kwargs[k] = kwargs[k]
            kwargs = new_kwargs

        return_objs = find(iterable, *rs, type_=cls, **kwargs)[:count]

        # If a particular number of items were requested, make sure
        # we return this exact number, otherwise raises an exception
        if count is not None and count > len(return_objs):
            raise CountError(
                '{count} {type}s were requested but only {lreturn}'
                ' were found. The requirements for the type of '
                '{type} were rs={rs} and kwargs={kwargs}'.format(
                    lreturn=len(return_objs),
                    type=cls.__name__,
                    rs=rs,
                    kwargs=kwargs,
                    count=count))
        # Return the specified amount
        return return_objs[:count]

    @property
    def testbed(self):
        try:
            testbed = self.__testbed__
        except AttributeError:
            raise AttributeError(
                "'%s' object has no '%s' attribute"
                % (self.__class__.__name__, 'testbed'))
        if testbed is not None:
            testbed = testbed()
        return testbed

    @testbed.setter
    def testbed(self, value):
        if value:
            self.__testbed__ = weakref.ref(value)
        else:
            self.__testbed__ = None

    def __repr__(self):
        try:
            name = self.name
        except:
            return '<%s object at 0x%x>' % (
                self.__class__.__name__,
                id(self))
        else:
            return '<%s object %r at 0x%x>' % (
                self.__class__.__name__,
                name,
                id(self))

    # By default, subclasses of Base are not hashable, thus not tracked.
    __hash__ = None


class ConfigurableBase(Base):
    """Base class for all configurable genie.conf objects

    Base class for all configurable objects of the genie.conf infrastructure.
    It contains the two mandatory functions.
    """

    # Default for all features is to have the same priority, at the lowest
    # possible position. Which is infinity
    _conf_priority = float('inf')

    @lookup('os', 'context')
    def build_config(self, *args, **kwargs):
        """Abstract method to build_config

        Api to build the configuration of an object. The configuration is built
        from the attribute of the object.

        Must be overwritten or an OS-specific version must be implemented, else
        will raise an exception.

        Args:
            None

        Return:
            None

        Raises:
            NotImplementedError
        """
        raise NotImplementedError('Method not implemented for %r with os %r'
                                  % (self, getattr(self, 'os', None)))

    @lookup('os', 'context')
    def build_unconfig(self, *args, **kwargs):
        """Abstract method to build_unconfig

        Api to remove the configuration of an object. The configuration is
        built from the attribute of the object.

        Must be overwritten or an OS-specific version must be implemented, else
        will raise an exception.

        Args:
            None

        Return:
            None

        Raises:
            NotImplementedError
        """
        raise NotImplementedError('Method not implemented for %r with os %r'
                                  % (self, getattr(self, 'os', None)))

    def _to_dict(self, value=None):
        from genie.conf.base.attributes import SubAttributesDict
        ret = {}
        for k, value in self.__dict__.items():
            # Disregard those, as cannot be compared between
            # run
            k = self._convert(self, k)
            #if k in ['devices', 'links', 'testbed', 'parent']:
            #    ret[k] = {}
            #    continue
            if isinstance(value, SubAttributesDict):
                # Its already a dict
                ret[k] = {}
                for k2, v2 in value.items():
                    ret[k][k2] = v2._to_dict(v2)
            else:
                ret[k] = value
        return ret

    def _convert(self, obj, var):
        '''Convert managed attribute name to expected'''
        # Check if it has _ at the front, and if it was added
        # as part of managedattribute
        try:
            needed = var.startswith('_')
        except AttributeError:
            return var

        no_underscore = var[1:]
        # check if it exists in the class
        if hasattr(self._find_parent_class(obj), no_underscore):
            return no_underscore
        return var

    def _find_parent_class(self, obj):
        '''Find the main parent class, its the one with managedattributes'''
        if hasattr(obj, 'parent'):
            return self._find_parent_class(obj.parent)
        return obj


class FeatureBase(ConfigurableBase):
    """Base class for all feature objects"""

    # Make all features hashable so their instances are tracked
    def __hash__(self):
        return hash(self.__class__.__name__)

    def _on_feature_devices_updated(self):
        '''Called when the `devices` list is updated.'''
        pass

    def _on_feature_interfaces_updated(self):
        '''Called when the `interfaces` list is updated.'''
        pass

    def _on_feature_links_updated(self):
        '''Called when the `links` list is updated.'''
        pass

    def _devices_with_feature(self):
        '''Called to determine the set of devices on which this feature is
        enabled in order to update the `devices` list.

        If overridding, call this method and add more devices.
        '''
        return set()

    def _interfaces_with_feature(self):
        '''Called to determine the set of interfaces on which this feature is
        enabled in order to update the `interfaces` list.

        If overridding, call this method and add more interfaces.
        '''
        return set()

    def _links_with_feature(self):
        '''Called to determine the set of links on which this feature is
        enabled in order to update the `links` list.

        If overridding, call this method and add more links.
        '''
        return set()

    def __eq__(self, other):
        # Check if same id
        if id(self) == id(other):
            # Same object
            return True
        # From same class
        if not isinstance(other, self.__class__):
            return False
        if self.testbed is not other.testbed:
            # If they arent in the same testbed,  then not equal
            return False

        return self.__dict__ == other.__dict__

        ## Now have to compare the managedattribute
        #for attribute in dir(self):
        #pass


class DeviceFeature(FeatureBase):
    """Base class for all device-based Feature objects

    Base class for all configurable device-based Feature objects.

    Contains a weaklist for all devices related to this `Feature`

    """

    @log_it
    def __init__(self, **kwargs):
        self._init_devices_list()
        super().__init__(**kwargs)

    def _init_devices_list(self):
        self.devices = WeakList()

    def _devices_with_feature(self):
        '''Called to determine the set of devices on which this feature is
        enabled in order to update the `devices` list.

        If overridding, call this method and add more devices.

        This particular implementation filters the `devices` list to confirm
        which still have the feature enabled.
        '''
        devices = set()
        for device in self.devices:
            if self in device.features:
                devices.add(device)
        return devices | super()._devices_with_feature()

    @log_it
    def _on_added_from_device(self, device):
        """Action to be taken when adding a feature to a device

        Action to be taken when adding a feature to a device. A feature
        can be part of multiple devices.

        Args:
            device (`Device`): device object

        Returns:
            `None`

        """
        if device not in self.devices:
            self.devices.append(device)
        self._on_feature_devices_updated()

    @log_it
    def _on_removed_from_device(self, device):
        """Action to be taken when removing a feature from a device

        Action to be taken when removing a feature from a device. A feature
        can be part of multiple devices.

        Args:
            `None`

        Returns:
            `None`

        """
        self.devices = WeakList(self._devices_with_feature())
        self._on_feature_devices_updated()

    def _on_feature_interfaces_updated(self):
        '''Called when the `interfaces` list is updated.

        This particular implementation updates the `devices` list.
        '''
        self.devices = WeakList(self._devices_with_feature())
        super()._on_feature_interfaces_updated()

    def _on_feature_links_updated(self):
        '''Called when the `links` list is updated.

        This particular implementation updates the `devices` list.
        '''
        self.devices = WeakList(self._devices_with_feature())
        super()._on_feature_links_updated()


class InterfaceFeature(FeatureBase):
    """Base class for all interface-based Feature objects

    Base class for all configurable interface-based Feature objects.

    Contains a weaklist for all interface related to this `Feature`

    """

    @log_it
    def __init__(self, **kwargs):
        self._init_interfaces_list()
        super().__init__(**kwargs)

    def _init_interfaces_list(self):
        self.interfaces = WeakList()

    def _interfaces_with_feature(self):
        '''Called to determine the set of interfaces on which this feature is
        enabled in order to update the `interfaces` list.

        If overridding, call this method and add more interfaces.

        This particular implementation filters the `interfaces` list to confirm
        which still have the feature enabled.
        '''
        interfaces = set()
        for interface in self.interfaces:
            if self in interface.features:
                interfaces.add(interface)
        return interfaces | super()._interfaces_with_feature()

    def _devices_with_feature(self):
        '''Called to determine the set of devices on which this feature is
        enabled in order to update the `devices` list.

        If overridding, call this method and add more devices.

        This particular implementation walks the `interfaces` list to find out
        which devices have the feature indirectly enabled.
        '''
        devices = set()
        for interface in self._interfaces_with_feature():
            devices.add(interface.device)
        return devices | super()._devices_with_feature()

    @log_it
    def _on_added_from_interface(self, interface):
        """Action to be taken when adding a feature to an interface

        Action to be taken when adding a feature to an interface. A feature
        can be part of multiple interfaces.

        Args:
            interface (`Interface`): interface object

        Returns:
            `None`

        """
        if interface not in self.interfaces:
            self.interfaces.append(interface)
        self._on_feature_interfaces_updated()

    @log_it
    def _on_removed_from_interface(self, interface):
        """Action to be taken when removing a feature from an interface

        Action to be taken when removing a feature from an interface. A feature
        can be part of multiple interfaces.

        Args:
            interface (`Interface`): interface object

        Returns:
            `None`

        """
        self.interfaces = WeakList(self._interfaces_with_feature())
        self._on_feature_interfaces_updated()

    def _on_feature_links_updated(self):
        '''Called when the `links` list is updated.

        This particular implementation updates the `interfaces` list.
        '''
        self.interfaces = WeakList(self._interfaces_with_feature())
        super()._on_feature_links_updated()


class LinkFeature(FeatureBase):
    """Base class for all link-based Feature objects

    Base class for all configurable link-based Feature objects.

    Contains a weaklist for all links related to this `Feature`

    """

    @log_it
    def __init__(self, **kwargs):
        self._init_links_list()
        super().__init__(**kwargs)

    def _init_links_list(self):
        self.links = WeakList()

    def _links_with_feature(self):
        '''Called to determine the set of links on which this feature is
        enabled in order to update the `links` list.

        If overridding, call this method and add more links.

        This particular implementation filters the `links` list to confirm
        which still have the feature enabled.
        '''
        links = set()
        for link in self.links:
            if self in link.features:
                links.add(link)
        return links | super()._links_with_feature()

    def _interfaces_with_feature(self):
        '''Called to determine the set of interfaces on which this feature is
        enabled in order to update the `interfaces` list.

        If overridding, call this method and add more interfaces.

        This particular implementation walks the `links` list to find out
        which interfaces have the feature indirectly enabled.
        '''
        interfaces = set()
        for link in self._links_with_feature():
            interfaces.update(link.interfaces)
        return interfaces | super()._interfaces_with_feature()

    def _devices_with_feature(self):
        '''Called to determine the set of devices on which this feature is
        enabled in order to update the `devices` list.

        If overridding, call this method and add more devices.

        This particular implementation walks the `links` list to find out
        which devices have the feature indirectly enabled.
        '''
        devices = set()
        for link in self._links_with_feature():
            devices.update(link.devices)
        return devices | super()._devices_with_feature()

    @log_it
    def _on_added_from_link(self, link):
        """Action to be taken when adding a feature to a link

        Action to be taken when adding a feature to a link

        Args:
            link (`Link`): link object

        Returns:
            `None`

        """
        if link not in self.links:
            self.links.append(link)
        self._on_feature_links_updated()

    @log_it
    def _on_removed_from_link(self, link):
        """Action to be taken when removing a feature from a link

        Action to be taken when removing a feature from a link

        Args:
            link (`Link`): link object

        Returns:
            `None`

        """
        self.links = WeakList(self._links_with_feature())
        self._on_feature_links_updated()
