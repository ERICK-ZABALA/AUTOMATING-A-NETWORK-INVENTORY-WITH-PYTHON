"""
:mod:`report` -- Report Element
======================================================

.. module:: report
   :synopsis: Report for TestSuite InitInfo
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements the report element for TestSuite InitInfo.

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.tsinitinfo.params.report.sem import SEM
from pyats.aereport.utils.argsvalidator import ArgsValidator

class Report (AEReportElement):
    """
        Class based on the following schema definition

    ::
    
        <xs:element name="report">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="type"></xs:element>
                    <xs:element name="sort" type="xs:boolean"></xs:element>
                    <xs:element name="outofrange" type="xs:boolean"></xs:element>
                    <xs:element name="uniquesuites" type="xs:boolean"></xs:element>
                    <xs:element name="sem"></xs:element>
                </xs:sequence>
            </xs:complexType>
        </xs:element>
    
    Attributes
    ----------
    tag : str
        Constant value = 'report' to be used as xml tag.
    type : str
        one of autotest, ats_easy, easypy, detail, or  summary. 
        In future we may add "html" type.
    sort : bool
        Enable/disable reporting of results in sorted order
    outofrange : bool
        Enable/disable reporting of out of range tasks
    uniquesuites : bool
        Enable/disable reporting of test suites as consolidated or 
        as unique when same suite is run multiple times with 
        different parameters
    sem : SEM
        SEM related configs
    """
    def __init__ (self):
        self.tag = 'report'
        self.type = ''
        self.sort = False
        self.outofrange = False
        self.uniquesuites = False
        self.count_common_result_summary = True
        self.sem = SEM()

    def set_args (self, **kwargs):
        """ Set params and children attributes (Report, SEM, MaxLimit)
        
        Parameters
        ----------
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
            Sem
        """
        args_def = [
                # initinfo
                ('type', 0,  str),
                ('sort', 0, bool),
                ('outofrange', 0, bool),
                ('uniquesuites', 0, bool),
                ('sem', 0, dict),
                    ]
        ArgsValidator.validate(args_def, **kwargs)
        if 'type' in kwargs:
            self.type = kwargs['type']
        if 'sort' in kwargs:
            self.sort = kwargs['sort']
        if 'outofrange' in kwargs:
            self.outofrange = kwargs['outofrange']
        if 'uniquesuites' in kwargs:
            self.uniquesuites = kwargs['uniquesuites']
        if 'sem' in kwargs:
            self.sem.set_args(**kwargs['sem'])
    
if __name__ == '__main__': # pragma: no cover
    rep = Report()
    rep.type = 'easypy'
    rep.sort = True
    rep.outofrange = False
    rep.uniquesuites = True
    rep.sem = SEM(**{'alignment': True, 'traceback': False})
    print(rep.xml())
