"""
:mod:`id` -- Id
===============

.. module:: id
   :synopsis: Id
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements Id element.

"""

from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.initinfo.id.idtims import IdTims
from pyats.aereport.utils.argsvalidator import ArgsValidator
import xml.etree.ElementTree as ET 
class Id (AEReportElement):
    '''
    Class based on this schema definition
    ::
    
        <xs:complexType name="idType">
            <xs:sequence>
                <xs:choice minOccurs="0">
                    <xs:element name="tc" type="xs:string"></xs:element>
                    <xs:element name="subtc" type="xs:string"></xs:element>
                </xs:choice>
                <xs:element name="variance" minOccurs="0"></xs:element>
                <xs:element name="tims" minOccurs="0"></xs:element>
                <xs:element name="testplan" minOccurs="0"></xs:element>
            </xs:sequence>
            <xs:attribute name="name" type="xs:string" use="required"></xs:attribute>
            <xs:attribute name="md5"></xs:attribute>
        </xs:complexType>
        
    Attributes
    ----------
    tag : str
        Default value = 'id'
    attrs : dict
        Dictionary of xml attributes:
        1- name: required
        2- md5
    idtypechoice : str
        Valid values are: 
        'tc': This is the testcase id in aetest context specified via -tc_id  to aetest::testcase API. For TIMS, this will be passed as case_id attribute.
        and 
        'subtc': This is the subtestcase id in aetest context for the  subtest and is specified via -subtc_id to aetest::subtest API. For TIMS, this will be passed as case_id attribute.
    idtypevalue : str
        The value of idtype
    variance : str
        Optional -  Variance id is the same as TIMS config id. 
        There cannot be a variance id at testcase level if it 
        contains subtests. In such case the variance id will 
        be part of subtest.
    tims : IdTims
        Tims id which is created and stored in TIMS
    testplan : str
        Optional - Test Plan id which should be an EDCS number
        
    '''
    def __init__ (self):
        self.tag = 'id'
        self.attrs = {'name': '', 'md5': ''}
        self.idtypechoice = 'tc' # Should be either tc or subtc
        self.idtypevalue = ''
        self.variance = None
        self.tims = None
        self.testplan = None  
                
    def generate_dom (self, parent):
        """ Override the default behavior of AEReportElement.generate_dom 
        
        Parameters
        ----------
        parent : AEReportElement
            The xml element that should be used as a parent
            for this userdef
        
        """
        dom_elt = ET.SubElement(parent, self.tag, self.get_unicode_attrs())
        choice = ET.SubElement(dom_elt, self.idtypechoice)
        choice.text = self.idtypevalue
        if self.variance:
            self.generate_simple_elt_dom(dom_elt, 'variance')
        if self.tims:
            self.tims.generate_dom(dom_elt)
        if self.testplan:
            self.generate_simple_elt_dom(dom_elt, 'testplan')

    def set_args (self, **kwargs):
        """ Set log file attributes
        
        Parameters
        ----------
        md5 : str
            Md5Id is calculated based on testcase name, test 
            parameters, testbed name etc to ensure uniqueness
        variance : str
            Variance id is the same as TIMS config id. There cannot be
            a variance id at testcase level if it contains subtests.
            In such case the variance id will be part of subtest.
        tims : dict
            Tims id which is created and stored in TIMS
        testplan : str
            Test Plan id which should be an EDCS number
        """

        args_def = [
                ('md5', 0, str),
                ('variance', 0, str),
                ('tims', 0, dict),
                ('testplan', 0, str)
                    ]
        ArgsValidator.validate(args_def, **kwargs)

        if 'md5' in kwargs:
            self.attrs['md5'] = kwargs['md5']
        if 'variance' in kwargs:
            self.variance = kwargs['variance']
        if 'tims' in kwargs:
            self.tims = IdTims()
            self.tims.set_args(**kwargs['tims'])
        if 'testplan' in kwargs:
            self.testplan = kwargs['testplan']
        if 'name' in kwargs:
            self.attrs['name'] = self.idtypevalue = kwargs['name']

if __name__ == '__main__': # pragma: no cover
    some_id = Id()
    some_id.attrs['name'] = 'id1'
    some_id.attrs['md5'] = 'A12132$%2343'
    some_id.idtypevalue = 'first_tc'
    tims1 = IdTims()
    tims1.case = 'case1'
    tims1.config = 'some tims configuration'
    some_id.tims = tims1
    some_id.testplan = 'EDCS-123456'
    print(some_id.xml())
