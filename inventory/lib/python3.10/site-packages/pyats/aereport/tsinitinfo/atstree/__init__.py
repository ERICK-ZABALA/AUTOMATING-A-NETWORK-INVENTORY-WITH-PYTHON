"""
:mod:`atstree` -- ATSTree
======================================================

.. module:: atstree
   :synopsis: ATSTree
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements ATSTree element.

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.tsinitinfo.atstree.atspackage import ATSPackage
from pyats.aereport.utils.argsvalidator import ArgsValidator

class ATSTree(AEReportElement):
    '''
        Class based on this schema definition

    ::
    
        <xs:element name="ats">
            <xs:annotation>
                <xs:documentation>ATS tree info</xs:documentation>
            </xs:annotation>
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="path"></xs:element>
                    <xs:element name="version"></xs:element>
                    <xs:element name="package" maxOccurs="unbounded">
                        <xs:annotation>
                            <xs:documentation>List of package names and corresponding version
                                loaded </xs:documentation>
                        </xs:annotation>
                        <xs:complexType>
                            <xs:sequence>
                                <xs:element name="name" />
                                <xs:element name="version" />
                            </xs:sequence>
                        </xs:complexType>
                    </xs:element>
                </xs:sequence>
            </xs:complexType>
        </xs:element>

    Attributes
    ----------    
    tag : str
        Constant value = 'ats' to be used as xml tag.        
    path : str
        The location of the ATS tree in which the test script is run.
    version : str
        The release version string found in the VERSION file of the root of the ATS tree.
    packages : list
        List of package names and corresponding version loaded
        
    '''
    def __init__(self):
        self.tag = 'ats'
        self.path = ''
        self.version = ''
        self.packages = [] # list of ats packages used

    def set_args (self, **kwargs):
        """ Set testsuite initinfo attributes
        
        Parameters
        ----------
        path : str
            The location of the ATS tree in which the test script is run.
        version : str
            The release version string found in the VERSION file of the root of the ATS tree
        packages : list    
            List of package names and corresponding version loaded

        Returns
        -------
        """
        args_def = [
                ('path', 0,  str),
                ('version', 0, str),
                ('packages', 0, list),
                    ]
        ArgsValidator.validate(args_def, **kwargs)
        if 'path' in kwargs:
            self.path = kwargs['path']
        if 'version' in kwargs:
            self.version = kwargs['version']
        if 'packages' in kwargs:
            for name,version in kwargs['packages']:
                self.packages.append(ATSPackage(**{'name':name,
                                                   'version':version}))

    def add_packages(self, kwargs):
        """ Add multiple packages to the ATS tree
        Accept list of format : [{name:'', version:''},....]
            
        
        Parameters
        ----------
        name : str
            Name of the package
        version : str
            Version of the package

        Returns
        -------
        """
        for name,version in kwargs:
            self.packages.append(ATSPackage(**{'name':name,
                                             'version':version}))
        
        
if __name__ == '__main__': # pragma: no cover
    from pyats.aereport.tsinitinfo.atstree.atspackage import ATSPackage
    atstree = ATSTree()
    atstree.path = '/path/to/ats/tree/'
    atstree.packages.append(ATSPackage(**{'name': 'csccon', 'version': 'v1.0'}))
    atstree.packages.append(ATSPackage(**{'name': 'log', 'version': 'v1.2'}))
    print(atstree.xml())
