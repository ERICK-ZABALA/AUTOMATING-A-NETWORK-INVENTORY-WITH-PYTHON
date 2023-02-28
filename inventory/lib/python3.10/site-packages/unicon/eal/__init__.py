"""
    Package:
        eal

    Description:
        Expect Abstraction Library (EAL) is a package which provides Tcl/Expect
        like API, using paramiko library as a backend. Paramiko is an open
        source python library for handling ssh connections. EAL uses paramiko's
        invoke_shell api to create an interactive shell session on the connected
        channel. Channel here, is a socket like object.

        EAL creates a shell session on the connected channel and uses stdin and
        stdout for interacting with it. It abstracts all the paramiko level
        configurations and exposes Expect like API's e.g send, expect, dialogs
        etc.

        The whole unicon uses EAL as backend for implementing APIs for
        device connection. In unicon framework, EAL is the lower most level of
        of abstraction for device interactions.
"""
