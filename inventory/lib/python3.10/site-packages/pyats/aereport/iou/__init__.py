"""
:mod:`iou` -- IOU
======================================================

.. module:: iou
   :synopsis: IOU and related elements
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module implement IOU section used by TestSuite.

"""
from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.infra import LogFile, Image
from pyats.aereport.iou.ioulive import IOULive
from pyats.aereport.iou.diou import DIOU
from pyats.aereport.iou.diou.ci import CI
from pyats.aereport.iou.iouinitinfo import IOUInitInfo


class IOU(AEReportElement):
    '''
        Iou server info started on local or remote hosts

        Class based on the following schema definition

    ::
    
        <xs:element name="iou" minOccurs="0" maxOccurs="unbounded">
        	<xs:complexType>
        		<xs:sequence>
        			<xs:element name="name"/>
        			<xs:element name="initinfo">...</xs:element>
        			<xs:element name="ioulive">...</xs:element>
        			<xs:element name="diou">...</xs:element>
        			<xs:element name="core" minOccurs="0">...</xs:element>
        		</xs:sequence>
        	</xs:complexType>
        </xs:element>
    
    Attributes
    ----------
    tag : str
        Default value = 'iou'.
        This is to ensure that all elements contain a tag attribute.
    name : str
        Name of the iou
    initinfo : IOUInitInfo
        info for iou
    image : Image
        Image object, containing name and full path to image
    ioulive : IOULive
        IOULive object
    diou : DIOU
        DIOU object
    core : str
        Core file name if iou crashes      

    '''
    def __init__ (self):
        self.tag = 'iou'
        self.name = ''
        self.image= Image()
        self.ioulive = IOULive()
        self.initinfo = IOUInitInfo()
        self.diou = DIOU()
        self.core = None
    
if __name__ == '__main__': # pragma: no cover
    iou = IOU()
    iou.name = 'some name'
    print(iou.xml())
