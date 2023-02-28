"""
:mod:`testscriptinitinfo` -- TestScriptInitInfo
======================================================

.. module:: testscriptinitinfo
   :synopsis: TestScriptInitInfo and related elements
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements TestScriptInitInfo section used by TestScript.

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.infra import LogFile
from pyats.aereport.testscriptinitinfo.script import Script
from pyats.aereport.testscriptinitinfo.testscriptaehandler import TestScriptAEHandler
from pyats.aereport.utils.argsvalidator import ArgsValidator

class TestScriptInitInfo(AEReportElement):
    '''
        Class based on this schema definition

    ::
    
        <xs:element name="initinfo">
        	<xs:complexType>
        		<xs:sequence>
        			<xs:element name="script"></xs:element>
        			<xs:element name="pargs" type="xs:string"></xs:element>
        			<xs:element name="taskid"></xs:element>
        			<xs:element name="description"></xs:element>
        			<xs:element name="logfile" type="LogFileType"></xs:element>
        			<xs:element name="swversion" minOccurs="0"/>
        			<xs:element name="hwversion" minOccurs="0"/>
        			<xs:element name="fwversion" minOccurs="0"/>
        			<xs:element name="tstversion" minOccurs="0"/>
        			<xs:element name="aehandler" minOccurs="0" maxOccurs="unbounded"></xs:element>
        		</xs:sequence>
        	</xs:complexType>
        </xs:element>
    
    Attributes
    ----------
    tag : str
        Default value = 'initinfo'
    script : Script
    pargs : str
    taskid : str
    description : str
    logfile : LogFile
    version : str
    swversion : str
        swversion 
    hwversion : str
        hwversion 
    fwversion : str
        fwversion 
    tstversion : str
        tstversion 
    aehandlers : list
        aehandlers - list of AEHandler
    '''
    def __init__(self):
        self.tag = 'initinfo'
        self.script = Script()
        self.pargs = ''
        self.taskid = ''
        self.description = ''
        self.logfile = LogFile()
        self.swversion = None # optional string
        self.hwversion = None # optional string
        self.fwversion = None # optional string
        self.tstversion = None # optional string
        self.aehandlers = [] # optional list of aehandlers

    def set_args (self, **kwargs):
        """ Set testscript set_args
        
        Parameters
        ----------
        # Initinfo 
        script : dict
            CLI paramerters passed to test script
        pargs : str
            CLI paramerters passed to test script
        taskid : str
            TaskId is set for easypy runs only; for stand-alone mode, it 
            would be null. This value is internally set by aetest::script_init
            API
        description : str
            Description for the testscript
        logfile : dict
            File in which the test script logs are saved
        swversion : str
            software version
        hwversion : str
            hardware version
        tstversion : str
            testscript version
        aehandlers : str
            aetest testcase or section handlers
        runinfo : dict
            Runinfo

        Returns
        -------
        """

        args_def = [
                ('script',0,dict),
                ('pargs',0,str),
                ('taskid',0,str),
                ('description',0,str),
                ('logfile',0,dict),
                ('swversion',0,str),
                ('hwversion',0,str),
                ('tstversion',0,str),
                ('aehandlers',0,list),
                   ]

        ArgsValidator.validate(args_def, **kwargs)

        if 'script' in kwargs:
            self.script.set_args(**kwargs['script'])
        if 'pargs' in kwargs:
            self.pargs = kwargs['pargs']
        if 'taskid' in kwargs:
            self.taskid= kwargs['taskid']
        if 'description' in kwargs:
            self.description= kwargs['description']
        if 'logfile' in kwargs:
            self.logfile.set_args(**kwargs['logfile'])
        if 'swversion' in kwargs:
            self.swversion=kwargs['swversion']
        if 'hwversion' in kwargs:
            self.hwversion=kwargs['hwversion']
        if 'tstversion' in kwargs:
            self.tstversion=kwargs['tstversion']
        if 'aehandlers' in kwargs:
            for aehandler in kwargs['aehandlers']:
                self.aehandlers.append(TestScriptAEHandler(**{'name':aehandler['name'],
                                                            'criteria':aehandler['criteria'],
                                                            'type':aehandler['type']}))

if __name__ == '__main__': # pragma: no cover
    tsii = TestScriptInitInfo()
    tsii.name = 'some name'
    tsii.taskid = 'task-1'
    tsii.version = 'v15.2'
    tsii.params = 'some params'
    tsii.logfile = LogFile(attrs={'begin': 10, 'size': 20})
    tsii.swversion = 'v1'
    tsii.hwversion = 'v2'
    tsii.fwversion = 'v3'
    tsii.tstversion = 'v4'
    tsii.aehandlers = [TestScriptAEHandler({'name': 'handler1', 'type': 'testcase'}),
                       TestScriptAEHandler({'name': 'handler2', 'type': 'section'})]
    print(tsii.xml())
