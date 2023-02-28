import os
from unicon.eal.expect import Spawn
from time import sleep
sec = 0.1 
print('spawning processes .....')
s1 = Spawn("telnet 10.64.70.24 2020")
s2 = Spawn("telnet 10.64.70.24 2019")

def waitpid():
    print('\ns1> waitpid for s1')
    ret = os.waitpid(s1.pid, os.WNOHANG)
    print(ret)

    print('s2> waitpid for s2')
    ret = os.waitpid(s2.pid, os.WNOHANG)
    print(ret)

def process():
    print('\ns1> ps command output')
    os.system("ps -eaf | grep -i %s| grep -v grep" % s1.pid)
    print('s2> ps command output')
    os.system("ps -eaf | grep -i %s| grep -v grep" % s2.pid)



print('sleeping for %s seconds ....' % sec)
sleep(sec)

print('\ns1> expect output ....')
s1.expect(r'.*')

print('\ns2> expect output ....')
s2.expect(r'.*')

process()
#waitpid()
