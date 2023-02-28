import sys

import pexpect

from unicon import patterns


start_prog = 'telnet 10.64.70.11'
hostname = r'^.*si-tvt-7200-28-42#$'

hdl = pexpect.spawnu(start_prog)
hdl.logfile = sys.stdout
hdl.expect(patterns.escape_char)
hdl.expect(patterns.username)
hdl.sendline('lab')
hdl.expect(patterns.password)
hdl.sendline('lab')
hdl.expect(hostname)

# config terminal
hdl.sendline('term length 0')
hdl.sendline('term width 0')
hdl.expect(hostname)

