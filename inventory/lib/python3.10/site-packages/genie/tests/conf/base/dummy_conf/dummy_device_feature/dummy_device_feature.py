from genie.conf.base import DeviceFeature

class Dummy(DeviceFeature):

    def build_config(self, devices=None, interfaces=None, links=None,
                     apply=True, attributes=None, **kwargs):
        pass

    def build_unconfig(self, devices=None, interfaces=None, links=None,
                       apply=True, attributes=None, **kwargs):
        pass
