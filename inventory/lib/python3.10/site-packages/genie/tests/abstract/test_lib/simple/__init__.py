from genie.abstract import lookup

class Ospf(object):
    
    os = 'nxos'
    
    @lookup('os')
    def abc(self):
        'abc'
        print('local')
        
    @lookup('os')
    def bcd(self):
        'bcd'
        print('local')
    
    def __call__(self):
        print('class OSPF defined in %s' % type(self).__module__)
