"""
:mod:`initinfo` -- InitInfo
======================================================

.. module:: initinfo
   :synopsis: InitInfo
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements InitInfo section (used by TestResult
and TestGroup), and its related elements Id and IdTims.

"""

from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.infra import LogFile, XRef
from pyats.aereport.initinfo.id import Id
from pyats.aereport.toplevel.simplelist import SimpleList
from pyats.aereport.utils.argsvalidator import ArgsValidator

class InitInfo(AEReportElement):
    '''
    Class based on this schema definition
    ::
        
        <xs:complexType name="initInfoType">
            <xs:sequence>
                <xs:element name="id">
                <xs:element name="name" type="xs:string">
                <xs:element name="xref" type="xrefType"/>
                <xs:element name="pargs" minOccurs="0"/>
                <xs:element name="description" type="xs:string">
                <xs:element name="uut" type="xs:string" minOccurs="0" maxOccurs="unbounded">
                <xs:element name="swversion" minOccurs="0"/>
                <xs:element name="hwversion" minOccurs="0"/>
                <xs:element name="fwversion" minOccurs="0"/>
                <xs:element name="tstversion" minOccurs="0"/>
                <xs:element name="logfile" type="LogFileType">
                <xs:element name="interface" minOccurs="0" maxOccurs="unbounded">
                <xs:element name="platform" minOccurs="0" maxOccurs="unbounded"> 
            </xs:sequence>
        </xs:complexType>
        
    Attributes
    ----------
    tag : str
        value = 'initinfo'
    id : `Id`
        Various ids related to testcase
    name : str
        Name of the testcase/subtest which is equivalent 
        of the Title attribute in TIMS
    xref : `XRef`
    pargs : str
    description : str
        Description for the testcase or subtest
    uuts : list(str)
        The logical name of the Unit Under Test
    swversion : str
        swversion 
    hwversion : str
        hwversion 
    fwversion : str
        fwversion 
    tstversion : str
        tstversion 
    logfile : `LogFile`
        File in which the testcase or subtest logs are saved.
        It could be same as test script log file
    interfaces : list(`Interface`)
    platform : list('platform')
        Platform element as provided by ats_resutls
    '''
    def __init__(self):
        self.tag = 'initinfo'
        self.id = Id() # TODO: Ask if 1 or many ids
        self.name = '' # equivalent to title attribute in TIMS
        self.xref = XRef()
        self.pargs = None # optional. TODO: Check if this is just a string
        self.description = ''
        self.uuts = [] #optional list of uuts [0:]
        self.swversion = None # optional string
        self.hwversion = None # optional string
        self.fwversion = None # optional string
        self.tstversion = None # optional string
        self.logfile = LogFile()
        self.uuts = SimpleList('uut')
        self.interfaces = SimpleList('interface')
        self.platforms = SimpleList('platform')

    def set_args (self, **kwargs):
        """ Set InitInfo attributes
        
        Parameters
        ----------
        name : str
            initinfo/name
        description : str
            initinfo/description
        pargs : str
            initinfo/pargs
        swversion : str
            initinfo/swversion
        hwversion : str
            initinfo/hwversion
        fwversion : str
            initinfo/fwversion
        tstversion : str
            initinfo/tstversion
        platform : str
            initinfo/platform
        interface : str
            initinfo/interface
        id : dict
        uut : str
        xref : dict
        logfile : dict
        
        Returns:
            None

        
        """
        args_def = [
                # initinfo
                ('description', 0,  str),
                ('fwversion', 0, str),
                ('hwversion', 0, str),
                ('swversion', 0, str),
                ('tstversion', 0, str),
                ('id', 0, dict), # tims, name, testplan, timsCase, timsConfig, md5
                ('interface', 0, str),
                ('logfile', 0, dict),
                ('name', 0, str),
                ('pargs', 0, str),
                ('platform', 0, str),
                ('uut', 0, str),
                ('xref', 0, dict),
                    ]
        ArgsValidator.validate(args_def, **kwargs)
        if 'description' in kwargs:
            self.description = kwargs['description'] or ''
        if 'fwversion' in kwargs:
            self.fwversion= kwargs['fwversion']
        if 'hwversion' in kwargs:
            self.hwversion= kwargs['hwversion']
        if 'swversion' in kwargs:
            self.swversion= kwargs['swversion']
        if 'tstversion' in kwargs:
            self.tstversion= kwargs['tstversion']
        if 'interface' in kwargs:
            self.interfaces.append(kwargs['interface'])
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'pargs' in kwargs:
            self.pargs = kwargs['pargs']
        if 'platform' in kwargs:
            self.platforms.append(kwargs['platform'])
        if 'uut' in kwargs:
            self.uuts.append(kwargs['uut'])
        if 'id' in kwargs:
            self.id.set_args(**kwargs['id'])
        if 'logfile' in kwargs:
            self.logfile.set_args(**kwargs['logfile'])
        if 'xref' in kwargs:
            self.xref.set_args(**kwargs['xref'])
    
if __name__ == '__main__': # pragma: no cover
    from pyats.aereport.initinfo.id.idtims import IdTims
    from pyats.aereport.initinfo.uut import UUT
    initinfo = InitInfo()
    initinfo.scriptname = 'my_script_name'
    initinfo.name = 'my_name'
    initinfo.scriptversion = 'v1.0.0'
    initinfo.description = 'here is some non useful description'
    initinfo.uuts.append('uut1')
    initinfo.uuts.append('uut2')
    some_id = Id()
    some_id.attrs['name'] = 'id1'
    some_id.attrs['md5'] = 'A12132$%2343'
    some_id.idtypevalue = 'first_tc'
    tims1 = IdTims()
    tims1.case = 'case1'
    tims1.config = 'some tims configuration'
    some_id.tims = tims1
    some_id.testplan = 'EDCS-123456'
    initinfo.id = some_id
    print(initinfo.xml())
