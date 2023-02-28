"""
:mod:`script` -- Script
======================================================

.. module:: Script
   :synopsis: script and related elements
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements Script section used by TestScript.

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.testscriptinitinfo.script.scm import SCM
from pyats.aereport.utils.argsvalidator import ArgsValidator

class Script(AEReportElement):
    '''
        Script Information of clean
        Class based on the following schema definition

    ::
    
        <xs:complexType name="scriptType">
        	<xs:sequence>
        		<xs:element name="name"></xs:element>
        		<xs:element name="path"></xs:element>
        		<xs:element name="version" type="xs:string" minOccurs="0"></xs:element>
        	</xs:sequence>
        </xs:complexType>

        OR 

        <xs:element name="script">
        	<xs:complexType>
        		<xs:sequence>
        			<xs:element name="name"></xs:element>
        			<xs:element name="path"></xs:element>
        			<xs:element name="scm" minOccurs="0"></xs:element>
        			<xs:element name="version" minOccurs="0"></xs:element>
        		</xs:sequence>
        	</xs:complexType>
        </xs:element>

    Attributes
    ----------
    tag : str
        Default value = 'script'.
        This is to ensure that all elements contain a tag attribute.
    name : str
        Script name 
    path : str
        Script path
    version : str
        Optional - Script version
    scm : SCM
        Optional - SCM info where the test script is checked in. Only available for 
        TestScriptInitInfo and not for Clean.
    '''

    def __init__(self, **kwargs):
        self.tag = 'script'
        self.name = ''
        self.path = ''
        self.version = None
        self.scm = None

    def set_args (self, **kwargs):
        """
        Set name, criteria and type of aehandler.
        
        Parameters
        ----------
        name : str
            Script name
        path : str
            Script Path
        scm : dict
            SCM info where the testscript is
            checked in
        version : str
            Script Version
            
        Returns
        -------
        
        """
        args_def = [
                ('name', 0,  str),
                ('path', 0,  str),
                ('scm', 0,  dict),
                ('version', 0,  str),
                   ]
        ArgsValidator.validate(args_def, **kwargs)
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'path' in kwargs:
            self.path = kwargs['path']
        if 'scm' in kwargs:
            if not self.scm:
                self.scm = SCM()
            self.scm.set_args(**kwargs['scm'])
        if 'version' in kwargs:
            self.version = kwargs['version']

if __name__ == '__main__': # pragma: no cover
    script = Script()
    script.name = 'aScriptName'
    script.path = '/a/script/path'
    script.version = 'aVersion'
    script.scm = SCM({'cvs': {'root':'cvs_root', 'repository': 'cvs_rep'}})
    print(script.xml())

