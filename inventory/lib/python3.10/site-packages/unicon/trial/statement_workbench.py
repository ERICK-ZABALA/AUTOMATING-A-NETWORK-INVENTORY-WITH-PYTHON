from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.dialog_processor import DialogProcessor
from inspect import getfullargspec as spec
from unicon.eal.expect import Spawn
from unicon.utils import AttributeDict

start1 = 'ls'
start2 = 'ps'

s1 = Spawn(start1)
# s2 = Spawn(start2)

pattern = '^pattern$'

def cb1():
    print('cb with no args')

def cb2(spawn, context):
    print('spawn=%s; context=%s' % (spawn, context))


def cb3(spawn, context, session, name):
    session.check = 'yes it works'
    session.num = 10
    print('spawn=%s; context=%s, session=%s; name=%s' % (spawn, context, session, name))


def cb4(spawn, city='bangalore'):
    print('spawn=%s; city=%s' % (spawn, city))


def cb5(spawn, context, session, name, city='bangalore', country='america'):
    print('spawn=%s; context=%s, name=%s; city=%s; contry=%s;' % (spawn, context, name, city, country))
    print(session.check)
    session.num *= session.num
    print('number is %s' % session.num)

s_list = [
    Statement(pattern=pattern, action=cb1),
    Statement(pattern=pattern, action=cb2),
    Statement(pattern=pattern, action=cb3, args={'name': 'person1'}),
    Statement(pattern=pattern, action=cb4),
    Statement(pattern=pattern, action=cb5, args={'name': 'person1', 'country': 'country1'}),
    Statement(pattern=pattern, action=None)
]

d = Dialog(s_list)

context = AttributeDict(dict(username='admin', password='lab'))

dp1 = DialogProcessor(d, s1, context)

dp1.process(context)



print('-- After dp1')
for st in d.statements:
    if st._action is not None:
        st._action()
for st in d.statements:
    if st._action is not None:
        st._action()

# dp2 = DialogProcessor(d, s2)
# print('-- After dp1')
# for st in d.statements:
#     if st._action is not None:
#         st._action()
#
#




# Issue:
# def sendline(spawn, command, timeout=10)
# Statement(pattern=pattern, action={'call': sendline, 'args': ['spawn', 'command'], 'kwargs':{'timeout':20}})

# Statement(pattern=pattern, action=sendline, args={command:'sh clock', timeout:10})
# convoluted mess of brackets and parenthesis
# difficult to perform static checks

# if call dict has no args or kwargs, and callable has arguments then something shall be done

# with action dict
# TC : try giving things which are not callable.
# TC : mention an arg which is not present in signature.
# TC : mention a kwargs which is not in signature.
# TC : if callable has args and action dict doesnt the it is a problem.
# TC : if all the arguments are not given in the action dict or normal callable then also it is an error condition.
# TC : callback has only default args, but still self.args overrides it
# TC : callback has only spawn and self.args is defined.
