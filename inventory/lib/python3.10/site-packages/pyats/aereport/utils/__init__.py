"""
:mod:`utils` -- Utilities module
======================================================

.. module:: utils
   :synopsis: contains helper classes and functions
    
.. moduleauthor: Ahmad Barghout <abarghou@cisco.com>

This module contains helper classes and functions.
"""

from datetime import timedelta
import os
import psutil

def print_block(block_title, block_content):
    """ Prints a formatted block with a title and content """
    print(''.join('=' * 80))
    print(block_title)
    print(''.join('-' * 80))
    print(block_content)
    print(''.join('=' * 80))
    print('\n')

def format_timedelta (tdelta):
    """ Given a timedelta object, it returns a string in
    the form: hh:mm:ss
    
    Parameters
    ----------
    tdelta : timedelta
    
    Returns
    -------
    str
        A string in the form hh:mm:ss
        
    """
    hours, rem = divmod(tdelta.seconds, 3600)
    hours = hours + (tdelta.days * 24)
    mins, secs = divmod(rem, 60)
    hours = format_time_portion(hours)
    mins = format_time_portion(mins)
    secs = format_time_portion(secs)
    return "%s:%s:%s" % (hours, mins, secs)
    
def format_time_portion (time_portion):
    """ Makes sure that a time portion (hours, minutes, seconds)
    is at least two digits. It doesn't accept negative values.
    
    Parameters
    ----------
    time_portion : int
        Value of hours or minutes or seconds
        
    Returns
    -------
    str
        A string of at least 2 digits
        
    """
    ret = "00"
    if time_portion > 0 and time_portion < 10:
        ret = "0" + str(time_portion)
    elif time_portion >= 10:
        ret = str(time_portion)
    return ret

def get_file_size (filepath):
    """ Gets the size of the provided file (in bytes)
        
    Parameters
    ----------
    filepath : str
        Path to the file
        
    Returns
    --------
    filesize : int
        Size of the file in bytes
    
    """
    filesize = os.path.getsize(filepath)
    return filesize

def get_file_name (filepath):
    """ Gets the file name portion of path/to/a/file
    Parameters
    ----------
    filepath : str
        Path to the file
        
    Returns
    --------
    filename : str
        Name of the file
    
    """
    filename = ''
    if filepath is not None and filepath != '':
        path_chunks = filepath.split('/')
        filename = path_chunks[-1]
    return filename

def get_ppid (pid):
    """
    Gets the parent process ID of the given process
    
    Parameters
    ----------
    pid : str or int
        Process ID

    Returns
    -------
    ppid : str
        Parent process ID as string
    
    Raises
    ------
    psutil.NoSuchProcess
        Raised when no process with the given PID is found
        in the current process list or when a process no
        longer exists (zombie)
    
    """
    pid = int(pid)
    _process=psutil.Process(pid)
    # This try catch is just for handling different versions of psutil
    # In v1.2.1 we should use ppid, whereas in v2.1.0 we should use ppid()
    try:
        ppid = _process.ppid()
    except:
        ppid = _process.ppid
    return str(ppid)
if __name__ == '__main__': # pragma: no cover
    print_block('my_title', 'hello this is me')
    td1 = timedelta(days=2, hours=3, seconds=50, minutes=4, microseconds=54)
    print_block('Testing timedelta', format_timedelta(td1))
    print(get_file_size("/tmp/output.xml"))
    print(get_file_name("/tmp/output.xml"))
    print(get_file_name(''))
