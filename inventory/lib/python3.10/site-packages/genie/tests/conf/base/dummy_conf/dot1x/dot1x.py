from genie.conf.base.base import DeviceFeature


class Dot1x(DeviceFeature):         

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_config(self, devices=None, apply=True, attributes=None,
                     **kwargs):
        pass

    def build_unconfig(self, devices=None, apply=True, attributes=None,
                       **kwargs):
        pass
