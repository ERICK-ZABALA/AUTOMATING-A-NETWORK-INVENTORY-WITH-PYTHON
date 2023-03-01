from genie import abstract
abstract.declare_token(__name__)


class Ospf(object):
    def do_work(self):
        return __name__
    class OspfChild(object):
        class OspfChildsChild(object):
            def do_work(self):
                return 'child.' + __name__
