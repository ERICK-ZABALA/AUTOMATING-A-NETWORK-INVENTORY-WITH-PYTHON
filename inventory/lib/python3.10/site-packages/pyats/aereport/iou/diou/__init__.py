"""
:mod:`diou` -- DIOU
======================================================

.. module:: diou
   :synopsis: DIOU
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implements DIOU section used by IOU

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.iou.diou.ci import CI

class DIOU(AEReportElement):
    """DIOU implements element used by IOU
        Class based on the following schema definition

    ::
    
        <xs:element name="diou">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="ci"></xs:element>
                </xs:sequence>
            </xs:complexType>
        </xs:element>        

    Attributes
    ----------
    tag : str
        Default value = 'notag'.
        This is to ensure that all elements contain a tag attribute.
    ci : CI()
        CI Object

    """
    def __init__ (self):
        self.tag = 'diou'
        self.ci = CI()
    
if __name__ == '__main__': # pragma: no cover
    diou = DIOU()
    print(diou.xml())
