"""
:mod:`tims` -- Tims 
======================================================

.. module:: tims
   :synopsis: Tims - Base Class
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements TIMS section used by TestSuite.

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.tims.timspost import TimsPost
from pyats.aereport.tims.timsattributes import TimsAttribute
from pyats.aereport.toplevel.simplelist import SimpleList
from pyats.aereport.utils.argsvalidator import ArgsValidator

class Tims(AEReportElement):
    """ This module implement Tims section used by TestSuite.
    If tims posting is enabled, this will contain result status of tims importer

    Class based on the following schema definition

    ::
    
        <xs:element name="tims">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="dnsname"></xs:element>
                    <xs:element name="attribute" maxOccurs="unbounded"></xs:element>
                    <xs:element name="post" type="TimsPostType"></xs:element>
                </xs:sequence>
                <xs:attribute name="bgPost" type="xs:boolean"></xs:attribute>
            </xs:complexType>
        </xs:element>        

    Attributes
    ----------
    tag : str
        Default value = 'notag'.
        This is to ensure that all elements contain a tag attribute.
    attrs : dict
        Default value is None.
        This is to ensure that all elements contain an attrs dictionary.
        `attrs` is expanded as attributes in the xml start tag.
    dnsname : str 
        TIMS token id
    attributes : SimpleList
        TIMS global attributes
    post : TimsPostType
        Status of ATS TIMS importer (if invoked) including the number
        of tests that were successfully posted to TIMS

    """
    def __init__ (self):
        self.tag = 'tims'
        self.attrs = {'bgPost':False}
        self.dnsname = ''
        self.attributes = [] 
        self.post= TimsPost()

    def set_args (self, **kwargs):
        """ Set attributes for tims
        
        Parameters
        ----------
        dnsname : str
            TIMS token id
        attributes : list
            TIMS global attributes
        post : dict
            Status of ATS TIMS importer (if invoked) including the number of tests that were successfully posted to TIMS
        bgPost : bool
            The attribute tracks is the posting to TIMS is done actively or is posted as an independent background task

        Returns
        -------
        """

        args_def = [
                ('dnsname', 0,  str),
                ('attributes', 0, list),
                ('post', 0,  dict),
                ('bgPost',0,bool),
                    ]
        ArgsValidator.validate(args_def, **kwargs)
        if 'bgPost' in kwargs:
            self.attrs['bgPost'] = kwargs['bgPost']
        if 'dnsname' in kwargs:
            self.dnsname = kwargs['dnsname']
        if 'post' in kwargs:
            self.post.set_args(**kwargs['post'])
        if 'attributes' in kwargs:
            for element in kwargs['attributes']:
                self.attributes.append(TimsAttribute())
                self.attributes[-1].set_args(**element)

if __name__ == '__main__': # pragma: no cover
    tims = Tims()
    tims.name = 'some dns'
    tims.set_args(attributes=[{'name':'aName',
                              'value':'aSuperValue'},
                              {'name':'secondName',
                              'value':'superValue2'}])
    print(tims.xml())
