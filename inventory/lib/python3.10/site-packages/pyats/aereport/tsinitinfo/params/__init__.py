"""
:mod:`params` -- Params
======================================================

.. module:: Params
   :synopsis: params
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements Params element.

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.tsinitinfo.params.maxlimit import MaxLimit
from pyats.aereport.tsinitinfo.params.report import Report
from pyats.aereport.tsinitinfo.params.report.sem import SEM
from pyats.aereport.utils.argsvalidator import ArgsValidator
import xml.etree.ElementTree as ET 

class Params(AEReportElement):
    '''
        Internally calculated "final" values of various parameters based on CLI, 
        control and CONFIG files (_easySetKey / _easyGetKey)
        
        Class based on this schema definition
        
    ::
    
        <xs:element name="params">
            <xs:annotation>
                <xs:documentation>internally calculated "final" values of various
                    parameters based on CLI, control and CONFIG files (_easySetKey /
                    _easyGetKey)</xs:documentation>
            </xs:annotation>
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="cli" type="xs:string"></xs:element>
                    <xs:element name="mailto"></xs:element>
                    <xs:element name="report"></xs:element>
                    <xs:element name="rerun" type="xs:boolean"></xs:element>
                    <xs:element name="cleantype" type="xs:string"></xs:element>
                    <xs:element name="uniquetid" type="xs:boolean"></xs:element>
                    <xs:element name="max"></xs:element>
                    <xs:element name="reason" />
                    <xs:choice minOccurs="0">
                        <xs:annotation>
                            <xs:documentation>List of tasks or suite lines requested 
                                for run
                            </xs:documentation>
                        </xs:annotation>
                        <xs:element name="tidRange"/>
                        <xs:element name="runLines"/>
                    </xs:choice>
                    <xs:element name="pause" type="xs:string" minOccurs="0"></xs:element>
                    <xs:element name="controlfile" type="xs:string" minOccurs="0"></xs:element>
                    <xs:element name="rerunfile" minOccurs="0"></xs:element>
                </xs:sequence>
            </xs:complexType>
        </xs:element>
        
    Attributes
    ----------
    tag : str
        Constant value = 'report' to be used as xml tag.
    cli : str
        CLI paramerters passed to easypy
    mailto : str
        List of users and mailing lists for e-mail notification
    report : Report    
    rerun : bool
        Enable/disable rerun mode
    cleantype : str
        Default value should be easyclean
    uniquetid : bool
        Enable/disable use of md5id for tid uniqueness
    max = MaxLimit
        Upper limit on the number of errors or forked jobs
    reason : str
    runchoice : str
        List of tasks or suite lines requested for run. 
        Value should be tidRange or runLines
    runchoicevalue : str
        The value to be used for runchoice
    pause : str
        The trigger value for pause: pass/fail - Optional
    controlfile : str
        Path and file name of queue file or control file - Optional
    rerunfile : str
        Name of rerun file if it exists - Optional
    
    '''
    def __init__(self):
        self.tag = 'params'
        self.cli = ''
        self.mailto = ''
        self.report = Report()
        self.rerun = False
        self.cleantype = 'easyclean'
        self.uniquetid = False
        self.max = MaxLimit()
        self.reason = ''
        # Need a or
        self.runchoice = 'tidRange' # Value should be either tidRange or runLines
        self.runchoicevalue = ''
        self.pause = None # optional string
        self.controlfile = None # optional string
        self.rerunfile = None # optional string

    def set_args (self, **kwargs):
        """ Set params and children attributes (Report, SEM, MaxLimit)
        
        Parameters
        ----------
        cli : str
            CLI paramerters passed to easypy
        mailto : str
            List of users and mailing lists for e-mail notification
        report : dict
            Report for testsuite
        rerun : bool 
            Enable/disable rerun mode
        cleantype : str
            Default value should be easyclean
        uniquetid : str
            Enable/disable use of md5id for tid uniqueness    
        max : dict
            Max errors and max jobs
        reason : str
            List of tasks or suite lines requested for run
        runchoice : str
            Choice between tidRange/runLines
        runchoicevalue : str
            Value of the above
        pause : str
            The trigger value for pause: pass/fail
        controlfile : str
            Path and file name of queue file or control file
        rerunfile : str
            Name of rerun file if it exists
        type : str
            one of autotest, ats_easy, easypy, detail, or  summary. In future we may add "html" type.
        sort : bool
            Enable/disable reporting of results in sorted order
        outofrange : bool
            Enable/disable reporting of out of range tasks
        uniquesuites : bool
            Enable/disable reporting of test suites as consolidated or
            as unique when same suite is run multiple times with different
            parameters
        sem : dict
            -
        alignment : bool
            Enable/disable reporting of SEM alignment errors
        traceback : bool
            Enable/disable reporting of SEM traceback errors
        errors : str
             max errors (default is 10)    
        jobs : str
            max jobs to fork per easypy harness (default is -1 no limit)

        Returns
        -------
        """
        args_def = [
                # initinfo
                ('cli', 0,  str),
                ('mailto', 0, str),
                ('report', 0, dict),
                ('rerun', 0, bool),
                ('cleantype', 0, str),
                ('uniquetid', 0, str),
                ('max', 0, dict),
                ('reason', 0, str),
                ('runchoice', 0, str),
                ('runchoicevalue', 0 ,str),
                ('pause', 0, str),
                ('controlfile', 0, str),
                ('rerunfile', 0, str),
                # To allow calling report from params
                # Without using a new dictionary
                ('type', 0,  str),
                ('sort', 0, bool),
                ('outofrange', 0, bool),
                ('uniquesuites', 0, bool),
                ('sem', 0, dict),
                # To allow sem being called 
                ('alignment',0,bool),
                ('traceback',0,bool),
                ('errors',0,str),
                ('jobs',0,str),
                    ]
        ArgsValidator.validate(args_def, **kwargs)

        if 'cli' in kwargs:
            self.cli = kwargs['cli']
        if 'mailto' in kwargs:
            self.mailto = kwargs['mailto']
        if 'report' in kwargs:
            self.report.set_args(**kwargs['report'])
        if 'rerun' in kwargs:
            self.rerun = kwargs['rerun']
        # TODO ??
        if 'cleantype' in kwargs:
            self.cleantype = kwargs['cleantype']
        if 'uniquetid' in kwargs:
            self.uniquetid = kwargs['uniquetid ']
        if 'max' in kwargs:
            self.max.set_args(**kwargs['max'])
        if 'reason' in kwargs:
            self.reason = kwargs['reason']
        # TODO : Choice here?
        if 'runchoice' in kwargs:
            self.runchoice = kwargs['runchoice']
        if 'runchoicevalue' in kwargs:
            self.runchoicevalue = kwargs['runchoicevalue']
        if 'pause' in kwargs:
            self.pause = kwargs['pause']
        if 'controlfile' in kwargs:
            self.controlfile = kwargs['controlfile']
        if 'rerunfile' in kwargs:
            self.rerunfile = kwargs['rerunfile']
        # To allow calling report from params
        # Without using a new dictionary
        if 'type' in kwargs:
            self.report.type = kwargs['type']
        if 'sort' in kwargs:
            self.report.sort = kwargs['sort']
        if 'outofrange' in kwargs:
            self.report.outofrange = kwargs['outofrange']
        if 'uniquesuites' in kwargs:
            self.report.uniquesuites = kwargs['uniquesuites']
        if 'sem' in kwargs:
            self.report.sem.set_args(**kwargs['sem'])
        # To allow calling sem from params
        # Without using a new dictionary
        if 'alignment' in kwargs:
            self.report.sem.alignment = kwargs['alignment']    
        if 'traceback' in kwargs:
            self.report.sem.traceback = kwargs['traceback']    
        # To allow calling maxlimit from params
        # Without using a new dictionary
        if 'errors' in kwargs:
            self.max.errors = kwargs['errors']    
        if 'jobs' in kwargs:
            self.max.jobs = kwargs['jobs']    

            

    def generate_dom (self, parent):
        """ Override the default behavior of AEReportElement.generate_dom 
        
        Parameters
        ----------
        parent : AEReportElement
            The xml element that should be used as a parent
            for this userdef
        
        """
        dom_elt = ET.SubElement(parent, self.tag, self.get_unicode_attrs())
        self.generate_simple_elt_dom(dom_elt, 'cli')
        self.generate_simple_elt_dom(dom_elt, 'mailto')
        self.report.generate_dom(dom_elt)
        self.generate_simple_elt_dom(dom_elt, 'rerun')
        self.generate_simple_elt_dom(dom_elt, 'cleantype')
        self.generate_simple_elt_dom(dom_elt, 'uniquetid')
        self.max.generate_dom(dom_elt)
        self.generate_simple_elt_dom(dom_elt, 'reason')
        runchoice = ET.SubElement(dom_elt, self.runchoice)
        runchoice.text = str(self.runchoicevalue)
        if self.pause:
            self.generate_simple_elt_dom(dom_elt, 'pause')
        if self.controlfile:
            self.generate_simple_elt_dom(dom_elt, 'controlfile')
        if self.rerunfile:
            self.generate_simple_elt_dom(dom_elt, 'rerunfile')
        
if __name__ == '__main__': # pragma: no cover
    from pyats.aereport.tsinitinfo.params.report.sem import SEM
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
    my_params.uniquetid = False
    my_params.max = MaxLimit(**{'errors': 20, 'jobs': 30})
    my_params.reason = 'some_reason'
    my_params.runchoice = 'tidRange'
    my_params.runchoicevalue = 'tidRangleValue'
    my_params.pause = None
    my_params.controlfile = '/path/to/control/file/'
    my_params.rerunfile = '/path/to/rerun/file/'
    print(my_params.xml())
