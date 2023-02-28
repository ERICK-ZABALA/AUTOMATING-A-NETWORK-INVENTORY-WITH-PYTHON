from pkg_resources import iter_entry_points

from .base import TestbedFileLoader

TOPOLOGY_LOADER_GROUP = "pyats.topology.loader"

def load(loadable = None, source = None, **kwargs):
    '''
    topology loader function

    Logic:
        - if source key is provided, look for entrypoint and load with kwargs
        - else load whatever loadable is

    Returns:
        loaded testbed object
    '''

    if source is not None:
        # user provided a custom source loader
        for ep in iter_entry_points(group=TOPOLOGY_LOADER_GROUP):

            # find the source action
            if ep.name == source:
                # found matching source loader
                loader = ep.load()

                # call the specified loader
                return loader(**kwargs).load()

        else:
            raise ValueError('Cannot find the specified topology source loader:'
                             ' %s. Did you install it to entry point %s?'
                             % (source, TOPOLOGY_LOADER_GROUP))

    else:
        # init with any passed processors (pre/markup/post)
        init_kwargs = {k: v for k, v in kwargs.items()
                       if k.endswith('processor')}
        # remove init kwargs from load kwargs
        for k in init_kwargs:
            kwargs.pop(k)

        return TestbedFileLoader(**init_kwargs).load(loadable, **kwargs)

