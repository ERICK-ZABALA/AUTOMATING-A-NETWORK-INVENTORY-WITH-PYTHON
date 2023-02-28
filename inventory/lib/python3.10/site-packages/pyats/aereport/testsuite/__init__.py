"""
:mod:`testsuite` -- TestSuite
======================================================

.. module:: testsuite
   :synopsis: TestSuite and Related Elements

.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module contains TestSuite and some of its child
elements.

"""
from pyats.utils.utils import get_time

from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.testsuite.jobexecution import JobExecution
from pyats.aereport.tsinitinfo import TSInitInfo
from pyats.aereport.tims import Tims
from pyats.aereport.runinfo import RunInfo
from pyats.aereport.results.summary import Summary
from pyats.aereport.iou import IOU
from pyats.aereport.utils.argsvalidator import ArgsValidator
from pyats.aereport.toplevel.simplelist import SimpleList
from pyats.aereport.testsuite.tsabort import TSAbort
from pyats.aereport.toplevel.decorators import log_it


class TestSuite(AEReportElement):
    ''' This is xml schema for test suite results corresponding to
    easypy job or suite invocation

        Class based on the following schema definition

    ::

        <xs:element name="starttime" type="xs:dateTime"></xs:element>
        <xs:element name="initinfo"></xs:element>
        <xs:element name="iou" minOccurs="0" maxOccurs="unbounded"></xs:element>
        <xs:element name="setupHandler" type="InfraHandlerSectionType" minOccurs="0" maxOccurs="unbounded"/>
        <xs:element name="clean" type="cleanType" minOccurs="0"></xs:element>
        <xs:element name="prerunHandler" type="InfraHandlerSectionType" minOccurs="0" maxOccurs="unbounded"/>
        <xs:element name="jobexecution"></xs:element>
        <xs:element name="postrunHandler" type="InfraHandlerSectionType" minOccurs="0" maxOccurs="unbounded"/>
        <xs:element name="tims"></xs:element>
        <xs:element name="mailAttachment" minOccurs="0" maxOccurs="unbounded"></xs:element>
        <xs:element name="reportHandler" type="InfraHandlerSectionType" minOccurs="0"/>
        <xs:element name="archivefile"></xs:element>
        <xs:element name="stoptime" type="xs:dateTime"></xs:element>
        <xs:element name="runtime"></xs:element>
        <xs:element name="summary" type="summaryType"/>
        <xs:element name="abort" minOccurs="0"></xs:element>

    Attributes
    ----------
    tag : str
        Constant value = 'testsuite' to be used as xml tag.
    starttime : datetime
        Time at which the job is invoked just before it locks
        testbed/image and does initialization. It should be the
        same as the timestamp used for creating the runinfo
        directory name: "job-timestamp"
    initinfo : TSInitInfo
    ious : list
        ious - list of IOU objects.
        Iou server info started on local or remote hosts
    setuphandlers : list
        setuphandlers - list of InfraHandlerSection objects
    clean : Clean
        clean routine prior to job execution
    prerunhandlers : list
        prerunhandlers - list of InfraHandlerSection objects
    jobexecution : JobExecution
        Job file execution information stored here
    postrunhandlers : list
        postrunhandlers - list of InfraHandlerSection objects
    tims : Tims
        If tims posting is enabled, this will contain result
        status of tims importer
    mailAttachments :list
        mailAttachments - list of MailAttachment objects.
        Pointer to the user generated  files for attaching to e-mail report.
    reporthandler : InfraHandlerSection
        reporthandler
    archivefile : str
        Pointer to the archive log file  (if one was requested) for the job
        run. It should be relative to root of ATS tree.
    stoptime : datetime
        Time at which the job completes, right after the report is
        generated and just befored it archives the results
    runtime : timedelta
    summary : Summary
    abort : Abort
        abort - Reports abort from user, abnormal script termination, etc.

    '''
    def __init__(self):
        self.tag = 'testsuite'
        self.starttime = get_time()
        self.initinfo = TSInitInfo()
        self.ious = [] # Optional list of IOU objects [0:]
        self.setuphandlers = [] # Optional list of InfraHandlerSectionType [0:]
        self.clean = None # Optional cleanType object
        self.prerunhandlers = [] # Optional list of InfraHandlerSectionType [0:]
        self.jobexecution = JobExecution()
        self.postrunhandlers = [] # Optional list of InfraHandlerSectionType [0:]
        self.tims = Tims()
        self.mailAttachments = SimpleList('mailAttachment')
        self.reporthandler = None # Optional InfraHandlerSectionType
        self.runinfo = RunInfo() #TODO: Check if this should exist here
        self.archivefile = ''
        self.stoptime = get_time()
        self.runtime = self.stoptime - self.starttime
        self.summary = Summary()
        self.abort = None # Optional

        self.children = [
                'starttime', 'initinfo', 'ious',
                'setuphandlers', 'clean', 'prerunhandlers',
                'jobexecution', 'postrunhandlers', 'tims',
                'mailAttachments', 'reporthandler', 'runinfo',
                'archivefile', 'stoptime', 'runtime',
                'summary', 'abort'
                         ]

    def __repr__ (self):
        return 'TestSuite(jobid=%s)' % self.initinfo.jobid

    def set_args (self, **kwargs):
        """ Set testsuite set_args

        Parameters
        ----------
        archivefile : str
            Pointer to the archive log file  (if one was requested) for the job run. It should be relative to root of ATS tree.
        abort : dict
            Reports abort from user, abnormal script termination, etc.
        ats : dict
            ATS tree info
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
        mailattachment: list
            Pointer to the user generated  files for attaching to e-mail report.

        Returns
        -------
        """

        args_def = [
                ('archivefile',0,str),
                # tsabort
                ('abort',0, dict),
                # initinfo
                ('ats',0,dict),
                ('CONFIG',0,str),
                ('host', 0, str),
                ('image', 0, str),
                ('jobid', 0, str),
                ('logfile', 0, dict),
                ('name', 0, str),
                ('owner', 0, str),
                ('params', 0,  dict),
                ('release', 0, str),
                ('submitter', 0, str),
                ('user', 0, str),
                ('testbed', 0, str),
                ('tbautoselect', 0, str),
                ('topology', 0, str),
                # Mailattachment
                ('mailAttachments',0,list),
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

        # setTsAbort
        # If already exists, do nothing
        if 'abort' in kwargs:
            if not self.abort:
                self.abort = TSAbort()
                self.abort.set_args(**kwargs['abort'])

        if 'archivefile' in kwargs:
            self.archivefile = kwargs['archivefile']

        if 'mailAttachments' in kwargs:
            self.mailAttachments.extend(kwargs['mailAttachments'])

        # SetInitInfo
        self.initinfo.set_args(**kwargs)

        # SetRunInfo
        self.runinfo.set_args(**kwargs)

    @log_it
    def get_infrahandler (self, tag, name):
        """
        Searches within infrahandlers lists whether an infrahandler
        of a given name already exists. It uses the tag to determine
        which list to search e.g. prerunhandlers list, etc.
        If the tag is reportHandler, the assigned value is returned
        regardless of name matching.

        Parameters
        ----------
        tag : str
            Used to determine which list to search. Possible values are:
            reportHandler, setupHandler, prerunHandler, and postrunHandler
        name : str
            The name of the handler to be found

        Returns
        -------
        ret : `InfraHandlerSection`
            InfraHandler if found; otherwise None

        """
        ret = None
        search_list = None
        if tag == 'reportHandler':
            # In case of reportHandler, there should be only one
            # so return it regardless of the name
            ret = self.reporthandler
        elif tag == 'setupHandler':
            search_list = self.setuphandlers
        elif tag == 'prerunHandler':
            search_list = self.prerunhandlers
        elif tag == 'postrunHandler':
            search_list = self.postrunhandlers

        if search_list:
            for ih in search_list:
                if ih.name == name:
                    ret = ih
                    break
        return ret

if __name__ == '__main__': # pragma: no cover
    from pyats.tests.aereport.entity_factory import EntityFactory as ef
    from datetime import timedelta
    ts1 = TestSuite()
    ts1.starttime = get_time()
    ts1.initinfo = ef.get_tsinitinfo()
    ts1.ious = [ef.get_iou(), ef.get_iou()]
    ts1.setuphandlers = [ef.get_infrahandlersection('setupHandler'),
                         ef.get_infrahandlersection('setupHandler')]
    ts1.clean = ef.get_clean()
    ts1.prerunhandlers = [ef.get_infrahandlersection('prerunHandler')]
    ts1.jobexecution = ef.get_jobexecution()
    ts1.postrunhandlers = [ef.get_infrahandlersection('postrunHandler')]
    ts1.tims = ef.get_tims()
    ts1.mailAttachments.append(ef.get_mailattachment())
    ts1.reporthandler = ef.get_infrahandlersection('reportHandler')
    ts1.runinfo = ef.get_runinfo()
    ts1.archivefile = 'some archive file'
    ts1.stoptime = get_time() - timedelta(hours=2)
    ts1.runtime = ts1.stoptime - ts1.starttime
    ts1.summary = ef.get_summary_detail()
    ts1.abort = ef.get_tsabort()
    print(ts1.xml())
