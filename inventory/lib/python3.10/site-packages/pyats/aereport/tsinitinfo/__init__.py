"""
:mod:`tsinitinfo` -- TSInitInfo
======================================================

.. module:: tsinitinfo
   :synopsis: TSInitInfo and related elements
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements TSInitInfo section used by TestSuite.

"""


from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.toplevel.simplelist import SimpleList
from pyats.aereport.infra import LogFile
from pyats.aereport.tsinitinfo.params import Params
from pyats.aereport.tsinitinfo.atstree import ATSTree
from pyats.aereport.utils.argsvalidator import ArgsValidator

class TSInitInfo(AEReportElement):
    '''
        Class based on this schema definition

    ::
        
        <xs:element name="initinfo">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="name" type="xs:string"></xs:element>
                    <xs:element name="params"></xs:element>
                    <xs:element name="jobid"></xs:element>
                    <xs:element name="ats"></xs:element>
                    <xs:element name="CONFIG"></xs:element>
                    <xs:element name="host" maxOccurs="unbounded"></xs:element>
                    <xs:element name="owner"></xs:element>
                    <xs:element name="submitter"></xs:element>
                    <xs:element name="user"></xs:element>
                    <xs:element name="topology"></xs:element>
                    <xs:element name="logfile"></xs:element>
                    <xs:element name="tbautoselect"></xs:element>
                    <xs:element name="release" />
                    <xs:element name="image" />
                    <xs:element name="testbed" />
                </xs:sequence>
            </xs:complexType>
        </xs:element>
        
    Attributes
    ----------    
    tag : str
        Constant value = 'ats' to be used as xml tag.
    name : str
        Name of testsuite
    params : Params
        internally calculated "final" values of various parameters based 
        on CLI, control and CONFIG files (_easySetKey / _easyGetKey)
    jobid : str
        JobId is a set of easypy runs only
    ats : ATSTree
        ATS tree info
    CONFIG : str
        Full path of CONFIG file that has been sourced
    hosts : SimpleList
        This is the value of TestHost keyword in autoetest context 
        and TRPhosts for easypy context. 
        It is the host on which easypy is executed.
    owner : str
        Owner of easypy (unix) process
    submitter : str
        Test submitter on whose behalf the job is run
    user : str
        userid of the current process/person launching `pyats run job`
    topology : str
        See Topomap xml schema for details -- testbed and device 
        info will be populated from CONFIG file
    logfile : LogFile
        File in which the job logs are saved
    tbautoselect : str
        List of Testbed names selected
    release : str
        Image Release
    image : str
        Image
    testbed : str
        Name of the tb
    path : str
        The location of the ATS tree in which the test script is run.
    version : str
        The release version string found in the VERSION file of the root of the ATS tree.
    packages : list
        List of package names and corresponding version loaded
    '''
    def __init__(self):
        self.tag = 'initinfo'
        self.name = ''
        self.params = Params()
        self.jobid = ''
        self.ats = ATSTree()
        self.CONFIG = ''
        self.hosts = SimpleList('host')
        self.owner = ''
        self.submitter = ''
        self.user= ''
        self.topology = ''
        self.logfile = LogFile()
        self.tbautoselect = ''
        self.release = ''
        self.image = ''
        self.testbed = ''

    def set_args (self, **kwargs):
        """ Set testsuite initinfo attributes
        
        Parameters
        ----------
        name : str
            Name of the testsuite
        params : dict
            internally calculated "final" values of various parameters
            based on CLI, control and CONFIG files (_easySetKey / _easyGetKey)
        report : dict
            Report for easypy/ats_easy/autotest
        logfile : dict
            File in which the job logs are saved
        release : str
            What is the release
        image : str
            path to image
        submitter : str
            Who submitted the testsuite
        user : str
            userid of the current process/person launching `pyats run job`
        tbautoselect : str
            List of Testbed names selected
        testbed : str
            Testbed selected
        jobid : str
            JobId is set for easypy runs only
        CONFIG : str
            Full path of CONFIG file that has been sourced
        host : str
            This is the value of TestHost keyword in autoetest context
            and TRPhosts for easypy context. It is the host on which easypy is executed.
        owner : str
            Owner of easypy (unix) process
        topology : str
            See Topomap xml schema for details -- testbed and device info will be populated from CONFIG file
        ats : dict
            ATS tree info
            
        Returns
        -------
        """
        args_def = [
                # initinfo
                ('name', 0, str),
                ('params', 0,  dict),
                ('logfile', 0, dict),
                ('release', 0, str),
                ('image', 0, str),
                ('submitter', 0, str),
                ('user', 0, str),
                ('tbautoselect', 0, str),
                ('testbed', 0, str),
                # Stuff not in aereport::initinfo
                ('jobid', 0, str),
                ('CONFIG', 0, str),
                ('host', 0, str),
                ('owner', 0, str),
                ('topology', 0, str),
                ('ats',0, dict),
                    ]
        ArgsValidator.validate(args_def, **kwargs)
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'params' in kwargs:
            self.params.set_args(**kwargs['params'])
        if 'logfile' in kwargs:
            self.logfile.set_args(**kwargs['logfile'])
        if 'release' in kwargs:
            self.release = kwargs['release']
        if 'image' in kwargs:
            self.image = kwargs['image']
        if 'submitter' in kwargs:
            self.submitter = kwargs['submitter']
        if 'user' in kwargs:
            self.user = kwargs['user']
        if 'tbautoselect' in kwargs:
            self.tbautoselect = kwargs['tbautoselect']
        if 'testbed' in kwargs:
            self.testbed = kwargs['testbed']
        if 'jobid' in kwargs:
            self.jobid = kwargs['jobid']
        if 'CONFIG' in kwargs:
            self.CONFIG = kwargs['CONFIG']
        if 'host' in kwargs:
            self.hosts.append(kwargs['host'])
        if 'owner' in kwargs:
            self.owner = kwargs['owner']
        if 'topology' in kwargs:
            self.topology = kwargs['topology']
        if 'ats' in kwargs:
            self.ats.set_args(**kwargs['ats'])

if __name__ == '__main__': # pragma: no cover
    from pyats.aereport.tsinitinfo.params.report.sem import SEM
    from pyats.aereport.tsinitinfo.params import Params
    from pyats.aereport.tsinitinfo.params.report import Report
    from pyats.aereport.tsinitinfo.params.maxlimit import MaxLimit
    from pyats.aereport.tsinitinfo.atstree.atspackage import ATSPackage
    
    atstree = ATSTree()
    atstree.path = '/path/to/ats/tree/'
    atstree.packages.append(ATSPackage(**{'name': 'csccon', 'version': 'v1.0'}))
    atstree.packages.append(ATSPackage(**{'name': 'log', 'version': 'v1.2'}))
    
    my_params = Params()
    my_params.tag = 'params'
    my_params.cli = 'some_cli'
    my_params.mailto = 'some_mailer'
    rep = Report()
    rep.type = 'easypy'
    rep.sort = True
    rep.outofrange = False
    rep.uniquesuites = True
    rep.sem = SEM(**{'alignment': True, 'traceback': False})
    my_params.report = rep
    my_params.rerun = False
    my_params.cleantype = 'easyclean'
    my_params.uniqueid = False
    my_params.max = MaxLimit(**{'errors': 20, 'jobs': 30})
    my_params.reason = 'some_reason'
    my_params.runchoice = 'tidRange'
    my_params.runchoicevalue = 'tidRangleValue'
#    print my_params.xml()
    
    lf = LogFile()
    lf.filepath = '/some/path/to/a/file/'
    lf.attrs['begin'] = 10
    lf.attrs['size'] = 512
    
    tsinit = TSInitInfo()
    tsinit.params = my_params
    tsinit.ats = atstree
    tsinit.CONFIG = 'CONFIG_FILE'
    tsinit.hosts.append('host1')
    tsinit.hosts.append('host2')
    tsinit.owner = 'abarghou'
    tsinit.submitter = 'jeaubin'
    tsinit.topology = 'topo1'
    tsinit.logfile = lf
    tsinit.tbautoselect = ''
    tsinit.release = 'rel1'
    tsinit.image = 'img2'
    tsinit.testbed = ''
    
    print(tsinit.xml())
