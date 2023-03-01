import os
import sys
import logging

from pyats.utils.yaml import Loader
from pyats.log.utils import banner

from pyats.topology.loader.markup import TestbedMarkupProcessor

from pyats.topology.schema import production_schema
from pyats.topology.exceptions import MissingDeviceError
from ..link import Link
from ..interface import BaseInterface as Interface
from ..device import Device
from ..testbed import Testbed


logger = logging.getLogger(__name__)


class TestbedFileLoader(Loader):
    '''TestbedFileLoader class

    Provides APIs & functionality to load YAML testbed files into corresponding
    testbed objects.

    Note
    ----
        this class is in effect a singleton.
    '''
    def __init__(self, enable_extensions = True):
        '''__init__ (built-in)

        instantiate parent Loader class by using custom schema,
        markup processor and post-processor.
        This allows loading testbed context info directly into testbed objects.
        '''

        # load and store the schema file internally.
        super().__init__(schema = production_schema,
                         enable_extensions = True,
                         markupprocessor = TestbedMarkupProcessor(),
                         postprocessor = self.create_testbed)


    def load_arbitrary(self, loadable, locations=None):
        # call generic YAML loader
        # ------------------------
        config = super().load_arbitrary(loadable, locations=locations)

        # apply defaults
        # --------------
        # force {} - yaml loads into None if there's no info
        config['testbed'] = config.get('testbed', None) or {}
        config['devices'] = config.get('devices', None) or {}
        config['topology'] = config.get('topology', None) or {}

        # apply default testbed file
        # --------------------------
        filename=None
        if isinstance(loadable, str) and os.path.isfile(loadable):
            filename = os.path.basename(loadable)
            config['testbed']['testbed_file'] = loadable
        else:
            try:
                # If loadable is a file-like object, then it has a
                # .name attribute.
                filename = os.path.basename(loadable.name)
                config['testbed']['testbed_file'] = loadable.name
            except AttributeError:
                logger.debug("Loadable {} does not have .name attribute.".\
                    format(loadable))

        # apply default testbed name
        # --------------------------
        try:
            name = config['testbed']['name']
        except (KeyError, TypeError):
            logger.debug("Deriving testbed name ...")
            if filename:
                if filename.startswith('CONFIG.'):
                    # name in the format of CONFIG.<tbname> (or other)
                    # assume last word is tb name
                    name = filename.split('.')[1]
                else:
                    # name in the format of <tbname>.yaml (or other)
                    # assume first word is testbed name
                    name = filename.split('.')[0]
            else:
                # no name provided
                name = ''
        finally:
            config['testbed']['name'] = name

        return config


    def create_testbed(self, config):
        ''' Transform a testbed configuration into a hierarchical object model.


        Parameters
        ----------
            config (dict): testbed configuration provided through loading

        Returns
        -------
            testbed (obj): object representing the loaded content.
        '''

        # convert config into Testbed objects
        # -----------------------------------
        # create Testbed object from testbed configs
        testbed = Testbed(**config['testbed'])

        # Add extends information to testbed, if user has provided it
        testbed.extends = config.get('extends', [])

        # create Device objects from device section, add to testbed
        for name, device in config['devices'].items():
            # expand device as kwargs
            testbed.add_device(Device(name = name, **device))

        # parse topology block
        #   1. find the link fields and replace the with actual link objects
        #   2. create interfaces and add them to links
        #   3. add interfaces to each device object.

        # track all the unique links in this topology
        links = {}

        # process if there's extended link information section
        if 'links' in config['topology']:
            # make sure to pop the links section so that it doesn't get
            # treated as a device
            for name, linkinfo in config['topology'].pop('links').items():
                links[name] = Link(name = name, **linkinfo)

        # process devices in topology section
        for device in config['topology']:
            if device not in testbed.devices:
                raise MissingDeviceError(device)

            interfaces = config['topology'][device]['interfaces']

            for name, intf in interfaces.items():
                if 'link' in intf:
                    # interface contains a link
                    linkname = intf['link']

                    if linkname not in links:
                        # discovered a new link in str format
                        links[linkname] = Link(name = linkname)

                    # make a copy of intf dict,
                    # replace the topology dict information with link objects
                    intf = intf.copy()
                    intf.update(link = links[linkname])

                # create the interface & add to device
                testbed.devices[device].add_interface(Interface(name = name,
                                                                **intf))
        # TBD - remove next release.
        if hasattr(testbed, 'iou'):
            logger.warning(banner("Topology key 'iou'\n"
                "is scheduled to be removed in the next release."))

        return testbed


# module = obj instance
sys.modules[__name__] = TestbedFileLoader()
