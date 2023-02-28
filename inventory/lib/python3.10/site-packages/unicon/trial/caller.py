"""
    It is just a caller script for Trackable Class
"""

from unicon.trial.trackables import Trackable

d = Trackable({
    'name': "vivek",
    'city': "Bangalore",
    'state': "Karnataka"
})

d.one = 1
d.two = 2
d['three'] = 3
