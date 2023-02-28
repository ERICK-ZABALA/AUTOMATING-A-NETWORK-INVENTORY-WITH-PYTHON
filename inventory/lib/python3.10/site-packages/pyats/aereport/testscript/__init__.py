"""
:mod:`testscript` -- TestScript Class
======================================================

.. module:: testscript
   :synopsis: TestScript Class and related elements

.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module TestScript Class and related elements.

"""
from pyats.utils.utils import get_time

from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.testscriptinitinfo import TestScriptInitInfo
from pyats.aereport.runinfo import RunInfo
from pyats.aereport.results.summary import Summary
from pyats.aereport.testscript.testresult import TestResult
from pyats.aereport.testscript.testgroup import TestGroup
from pyats.aereport.testscript.testsection import TestSection
from pyats.aereport.handlers import InfraHandlerSection

from pyats.aereport.utils import get_file_size
from pyats.aereport.utils.argsvalidator import ArgsValidator
from pyats.aereport import LoggingMode
from pyats.aereport.toplevel.decorators import log_it

from pyats.aereport.exceptions.aereport_errors import NoConnectionError

class TestScript (AEReportElement):
    """ One or more test scripts that are invoked by the job file
        Class based on the following schema definition

    ::

        <xs:element name="testscript" minOccurs="0" maxOccurs="unbounded">
            <xs:annotation>
                <xs:documentation>One or more test scripts that are
                    invoked by the job file</xs:documentation>
            </xs:annotation>
            <xs:complexType>
                <xs:complexContent>
                    <xs:extension base="TestScriptType">
                        <xs:sequence>
                            <xs:element name="pretestHandler" type="InfraHandlerSectionType"
                                minOccurs="0" maxOccurs="unbounded"/>
                            <xs:element name="starttime" type="xs:dateTime"></xs:element>
                            <xs:element name="initinfo"></xs:element>
                            <xs:element name="runinfo" type="runinfoType" />
                            <xs:element name="commonSetup" type="TestSectionType"
                                minOccurs="0"></xs:element>
                            <xs:element name="commonVerify" type="TestSectionType"
                                minOccurs="0"></xs:element>
                            <xs:element name="testcase" type="TestResultType"
                                minOccurs="0" maxOccurs="unbounded"></xs:element>
                            <xs:element name="commonCleanup" type="TestSectionType"
                                minOccurs="0"></xs:element>
                            <xs:element name="stoptime" type="xs:dateTime"></xs:element>
                            <xs:element name="runtime"></xs:element>
                            <xs:element name="summary" type="summaryType" />
                            <xs:element name="posttestHandler" type="InfraHandlerSectionType"
                                minOccurs="0" maxOccurs="unbounded"></xs:element>
                            <xs:element name="cleanonerror" type="cleanType"
                                minOccurs="0"></xs:element>
                            <xs:element name="pause" minOccurs="0"></xs:element>
                            <xs:element name="abort" minOccurs="0"></xs:element>
                        </xs:sequence>
                    </xs:extension>
                </xs:complexContent>
            </xs:complexType>
        </xs:element>

    Attributes
    ----------
    tag : str
        Constant value = 'testscript' to be used as xml tag.
    pretesthandlers : list
        Optional - list of InfraHandlerSection
    starttime : datetime
        Initalized by aetest::script_init API
    initinfo : TestScriptInitInfo
    runinfo : RunInfo
    commonSetup : TestSection
        Optional - This is the section to configure the devices which is common
        for all the testcases in the script and is enclosed within
        aetest::common_setup API. All logs go into test script log file
    commonVerify : TestSection
        Optional - This section is for verification invoked via
        aetest::common_verify API. All logs go into test script log file
    testcases : list
        Optional - list of TestResultType
    commonCleanup : TestSection
        Optional - This section is invoked via aetest::common_cleanup API
        and ensures that the steps occuring in common setup and
        verify are unconfigured here. All logs go into test script
        log file.
    commonModify : TestSection
        Optional - This section is invoked via aetest::common_modify API
    stoptime : datetime
        Initalized by aetest::end API?
    runtime : timedelta
    summary : Summary
    posttestHandler : list
        Optional - list of InfraHandlerSection. Autoeasy post test handler
    cleanonerror : Clean
        Optional - clean routine on error condition
    pause : Pause
        Optional - Invoked at the end of the testscript
    abort : TestScriptAbort
        Optional


    """
    def __init__ (self, logfilepath, logging):
        self.tag = 'testscript'
        self.pretesthandlers = []
        self.starttime = get_time()
        self.initinfo = TestScriptInitInfo()
        self.runinfo = RunInfo()
        self.commonSetup = []
        self.commonVerify = []
        self.commonModify = []
        self.testcases = []
        self.commonCleanup = []
        self.stoptime = get_time()
        self.runtime = None
        self.summary = Summary()
        self.posttesthandlers = []
        self.cleanonerror = None
        self.pause = None
        self.abort = None

        self.children = [
            'pretesthandlers', 'starttime', 'initinfo',
            'runinfo', 'commonSetup', 'commonVerify',
            'testcases', 'commonCleanup', 'stoptime',
            'runtime', 'summary', 'posttesthandlers',
            'cleanonerror', 'pause', 'abort','commonModify',
                        ]
        self._logging = logging
        self.initinfo.logfile.filepath = logfilepath

    def get_testcase (self, tcid):
        """
        Verify if a testcase exists, if so return it, else return None

        Parameters
        ----------
        tcid : str
            The id of the testcase to be found

        Returns
        -------
            str or None
                If testcase exists, return the testcase. Else None.
        """
        ret = None
        if self.testcases:
            for tc in self.testcases:
                if tc.initinfo.id.attrs['name'] == tcid:
                    ret = tc
                    break
        return ret

    def get_subtest (self, subtcid):
        """
        Verify if a subtest exists, if so return it, else return None

        Parameters
        ----------
        subtcid : str
            The id of the subtest to be found.

        Returns
        -------
            str or None
                If testcase exists, return the testcase. Else None.
        """
        ret = None
        if self.testcases:
            for tc in self.testcases:
                for subtc in tc.subtests:
                    if subtc.initinfo.id.attrs['name'] == subtcid:
                        ret = subtc
                        break
        return ret

    def get_logging_mode (self):
        """
        Return the logging mode

        Returns
        -------
            str
                Logging mode
        """
        return self._logging

    def add_testcase (self, **kwargs):
        """
        Create a testcase (TestResult) and append it to
        the testcases list.

        Parameters
        ----------
        tcid : str
            The id of the testcase to be created. This is set once
            and never overwritten
        variance : str
            Optional -  Variance id is the same as TIMS config id.
            There cannot be a variance id at testcase level if it
            contains subtests. In such case the variance id will
            be part of subtest.
        name : str
            Name of the testcase/subtest which is equivalent
            of the Title attribute in TIMS
        xref : dict
            xRef
        id : dict
            id of the testcase

        """
        args_def = [
            ('tcid', 1, str),
            ('logfilepath', 1, str),
            ('variance', 0, str),
            ('name', 0, str),
            ('xref', 0, dict),
            ('id', 0, dict),
                    ]
        ArgsValidator.validate(args_def, **kwargs)
        tc = TestResult(**kwargs)
        tc.set_args(**kwargs)
        self.testcases.append(tc)
        return tc

    def is_last_testcase_closed (self):
        """
        Return if the last testcase is closed

        Returns
        -------
            Bool
                Return 1 if last testcase was closed,  else False
        """
        ret = True
        if self.testcases:
            if not self.testcases[-1].isstopped():
                ret = False
        return ret

    def get_testsection (self, id):
        """
        Return the testsection

        Returns
        -------
            str or None
                If common<...> return section string,  else return None
        """
        ret = None
        if self.commonSetup:
            for section in self.commonSetup:
                if section.name == id:
                    ret = section
                    return ret
        if self.commonVerify:
            for section in self.commonVerify:
                if section.name == id:
                    ret = section
                    return ret
        if self.commonCleanup:
            for section in self.commonCleanup:
                if section.name == id:
                    ret = section
                    return ret
        if self.commonModify:
            for section in self.commonModify:
                if section.name == id:
                    ret = section
                    return ret
        return ret

    def is_last_testsection_closed (self):
        """
        Return if the last testsection is closed

        Returns
        -------
            Bool
                Return 1 if last testsection was closed,  else False
        """
        ret = True
        if self.commonSetup:
            if not self.commonSetup[-1].isstopped():
                ret = False
        if self.commonVerify:
            if not self.commonVerify[-1].isstopped():
                ret = False
        if self.commonCleanup:
            if not self.commonVerify[-1].isstopped():
                ret = False
        if self.commonModify:
            if not self.commonModify[-1].isstopped():
                ret = False
        return ret

    def add_testsection (self, **kwargs):
        """
        Create a testsection (TestSection) and append it to
        the sections list.

        Parameters
        ----------
        sectionid : str
            The id of the section to be created. This is set once
            and never overwritten
        logfilepath : str
            Path to the log file for the testcase
        name : str
            Name of the testsection

        Returns
        -------
            str or None
                Return the section if common<..> else return None

        """
        args_def = [
            ('sectionid', 1, str),
#            ('logfilepath', 1, str),
            ('name', 0, str),
            ('xref', 0, dict),
            ('id', 0, dict),
                    ]
        ArgsValidator.validate(args_def, **kwargs)

        if 'sectionid' in kwargs:
            section = TestSection(kwargs['sectionid'])
            section.set_args(**kwargs)
            if 'commonSetup' in kwargs['sectionid']:
                self.commonSetup.append(section)
                return section
            if 'commonVerify' in kwargs['sectionid']:
                self.commonVerify.append(section)
                return section
            if 'commonCleanup' in kwargs['sectionid']:
                self.commonCleanup.append(section)
                return section
            if 'commonModify' in kwargs['sectionid']:
                self.commonModify.append(section)
                return section
        return None

    @log_it
    def get_infrahandler (self, tag, name):
        """
        Searches within infrahandlers lists whether an infrahandler
        of a given name already exists. It uses the tag to determine
        which list to search e.g. pretesthandlers list, etc.

        Parameters
        ----------
        tag : str
            Used to determine which list to search. Possible values are:
            pretestHandler and posttestHandler
        name : str
            The name of the handler to be found

        Returns
        -------
        ret : `InfraHandlerSection`
            InfraHandler if found; otherwise None

        """
        ret = None
        search_list = None
        if tag == 'pretestHandler':
            search_list = self.pretesthandlers
        elif tag == 'posttestHandler':
            search_list = self.posttesthandlers

        if search_list:
            for ih in search_list:
                if ih.name == name:
                    ret = ih
                    break
        return ret

    def start_logfile (self, filepath):
        """
        Sets the logfile path, and if logging is set to SingleFile,
        it calculates the size of the logfile at
        that moment, and uses the value for 'begin'
        attribute of logfile

        Parameters
        ----------
        filepath : str
            Path to the log file to be used

        """
        logfile = self.initinfo.logfile
        logging_mode = self.get_logging_mode()
        logfile.filepath = filepath
        if logging_mode == LoggingMode.SingleFile:
            logfile_size = get_file_size(filepath)
            logfile.attrs['begin'] = logfile_size

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
        initinfo : dict
            Initinfo
        runinfo : dict
            runinfo

        Note
        ----
        Clean is not supported by aetest,  hence not supported by aereport.
        However, the clean API is working,  and can be easily enhanced to
        support clean in testscript. It is working right now for testsuite.

        """

        args_def = [
                # initinfo
                ('script',0,dict),
                ('pargs',0,str),
                ('taskid',0,str),
                ('description',0,str),
                ('logfile',0,dict),
                ('swversion',0,str),
                ('hwversion',0,str),
                ('aehandlers',0,dict),
                # runinfo
                ('abort', 0, dict),
                ('comment', 0, str),
                ('diag', 0, str),
                ('error', 0, dict),
                ('userDef', 0, dict),
                ('pause', 0, dict),
                ('unpause', 0, [int, str]),
                   ]

        ArgsValidator.validate(args_def, **kwargs)

        # SetInitInfo
        self.initinfo.set_args(**kwargs)

        # SetRunInfo
        self.runinfo.set_args(**kwargs)

    def __repr__ (self):
        return "TestScript(taskid='%s', name='%s')" % (self.initinfo.taskid,
                                                self.initinfo.script.name)

if __name__ == '__main__': # pragma: no cover
    from pyats.aereport.testscript.testsection import TestSection
    from pyats.aereport.infra import Pause
    from pyats.aereport.testscript.testscriptabort import TestScriptAbort

    ts1 = TestScript()
    ts1.pretesthandlers = [InfraHandlerSection('pretestHandler')]
    ts1.starttime = get_time()
    ts1.initinfo = TestScriptInitInfo()
    ts1.runinfo = RunInfo()
    ts1.commonSetup = TestSection('commonSetup')
    ts1.commonVerify = TestSection('commonVerify')
    ts1.testcases = []
    ts1.commonCleanup = TestSection('commonCleanup')
    ts1.stoptime = get_time()
    ts1.runtime = ts1.stoptime - ts1.starttime
    ts1.summary = Summary()
    ts1.posttesthandlers = [InfraHandlerSection('pretestHandler')]
    ts1.pause = Pause()
    ts1.abort = TestScriptAbort()
    print(ts1.xml())
