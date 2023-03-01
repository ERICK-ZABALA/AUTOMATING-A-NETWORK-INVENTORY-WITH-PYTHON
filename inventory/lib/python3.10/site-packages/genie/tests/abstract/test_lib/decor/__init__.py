from genie.abstract import lookup


class Ospf(object):

    def __init__(self, os, serie, type):
        self.os = os
        self.serie = serie
        self.type = type

    @lookup('os', 'serie', 'type')
    def do_work(self):
        raise NotImplementedError


    class OspfChild(object):
        class OspfChildsChild(object):
            def __init__(self, os, serie, type):
                self.os = os
                self.serie = serie
                self.type = type

            @lookup('os', 'serie', 'type')
            def do_work(self):
                raise NotImplementedError
