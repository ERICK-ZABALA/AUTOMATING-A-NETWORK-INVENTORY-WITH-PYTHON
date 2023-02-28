"""
:mod:`runinfo` -- RunInfo
======================================================

.. module:: runinfo
   :synopsis: RunInfo and Related Elements
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com> Jean-Benoit Aubin <jeaubin@cisco.com>

This module contains the RunInfo class that is used by several AEReport 
elements such as TestScript, TestSection, TestResult, etc.

"""

from pyats.aereport.toplevel.aereportelement import AEReportElement
from pyats.aereport.toplevel.simplelist import SimpleList
from pyats.aereport.infra import Pause, XRef
from pyats.aereport.runinfo.abort import Abort
from pyats.aereport.runinfo.userdef import UserDef
from pyats.aereport.utils.argsvalidator import ArgsValidator

class RunInfo(AEReportElement):
    """
        Class based on the following schema definition

    ::
    
        <xs:complexType name="runinfoType">
            <xs:sequence minOccurs="0" maxOccurs="unbounded">
                <xs:element name="comment" minOccurs="0" />
                <xs:element name="diag" minOccurs="0" />
                <xs:element name="error" type="xrefType" minOccurs="0" />
                <xs:element name="pause" minOccurs="0"></xs:element>
                <xs:element name="abort" minOccurs="0"></xs:element>
                <xs:element name="device" minOccurs="0"></xs:element>
                <xs:element ref="userDef" minOccurs="0" />
            </xs:sequence>
        </xs:complexType>
        
    Attributes
    ----------
    tag : str
        Constant value = 'runinfo' to be used as xml tag.
    comments : list
        Optional - list of strings
    diags : list
        Optional - list of strings
    errors : list
        Optional - list of XRef
    pauses : list
        Optional - list of Pause
    abort : Abort
        Optional
    device : Device
        Optional
    userDefs : list
        Optional - list of UserDef
    
    """
    def __init__(self):
        self.tag = 'runinfo'
        self.comments = SimpleList('comment')
        self.diags = SimpleList('diag')
        self.errors = []
        self.pauses = []
        self.abort = None
        self.device = None
        self.userDefs = [] 
           
    def set_args (self, **kwargs):
        """ Set testsuite initinfo attributes
        
        Parameters
        ----------
        comment : str or int
            Comment for the run
        diag : str
            Diag for the run
        error : str
            Error for the run
        userdef: str
            User defined tag
        pause : str
            pause
        unpause: str
            Unpause
            
        """
        args_def = [
                ('comment', 0,  str),
                ('diag', 0, str),
                ('error', 0, dict),
                ('userDef', 0, dict),
                ('pause', 0, dict),
                ('unpause', 0, [int, str])
                    ]
        ArgsValidator.validate(args_def, **kwargs)
        if 'comment' in kwargs:
            self.comments.append(kwargs['comment'])
        if 'diag' in kwargs:
            self.diags.append(kwargs['diag'])
        if 'error' in kwargs:
            self.errors.append(XRef('error'))
            self.errors[-1].set_args(**kwargs['error'])
        if 'abort' in kwargs:
            self.abort = Abort()
            self.abort.set_args(**kwargs['abort'])
        if 'userDef' in kwargs:
            self.userDefs.append(UserDef())
            self.userDefs[-1].set_args(**kwargs['userDef'])
        if 'pause' in kwargs:
            if self.pauses == [] or self.pauses[-1].isstopped():
                self.pauses.append(Pause())
            self.pauses[-1].set_args(**kwargs['pause'])
        if 'unpause' in kwargs:
            if self.pauses[-1].isstarted():
                self.pauses[-1].stop()
            else : 
                print ('Warning : Unpausing without having a pause is not'
                                  ' permitted')

if __name__ == '__main__': # pragma: no cover
    from pyats.aereport.infra import XRef, Pause
    from pyats.aereport.runinfo.abort import Abort
    from pyats.aereport.runinfo.device import Device
    from pyats.aereport.runinfo.userdef import UserDef
    ri1 = RunInfo()
    ri1.comments.append('Here I have some comment')
    ri1.diags.append('This is a dialog')
    ri1.errors.append(XRef('error'))
    ri1.pauses.append(Pause())
    ri1.abort = Abort()
    ri1.device = Device()
    ri1.userDefs.append(UserDef())
    print(ri1.xml())
    
    ri2 = RunInfo()
    ri2.set_args(pause='some_diag')
    print(ri2.xml())
