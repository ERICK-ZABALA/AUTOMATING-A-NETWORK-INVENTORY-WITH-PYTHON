"""
    A dict which keeps a log about when and where it was
    modified.
"""
import inspect

# class Trackable():

#     def __init__(self, data={}):
#         self._data = data

#     def __setattr__(self, key, value):
#         print("setattr - %s - %s" % (key, value))
#         super().__setattr__(key, value)
#         if key != '_data':
#             self._data[key] = value

#     def get(self, key):
#         return self._data[key]

#     def set(self, key, value):
#         self._data[key] = value


class Trackable(dict):

    def __init__(self, d={}):
        super().__init__(d)
        self.__dict__.update(self)
        self._history = {}

    def __setitem__(self, key, value):
        if key == '__dict__' or key == '_history':
            print('setitem skipped - %s - %s' % (key, value))
        else:
            print('setitem - %s -  %s' % (key, value))
            curframe = inspect.currentframe()
            outerframe = inspect.getouterframes(curframe, 2)
            self._history[key] = "value=%s, file=%s, line=%s" % (
                value, outerframe[1][1], outerframe[1][2])
            self.__dict__[key] = value
        super().__setitem__(key, value)

    def __setattr__(self, key, value):
        if key == '__dict__' or key == '_history':
            print('setattribute skipped - %s - %s' % (key, value))
        else:
            print('setattribute - %s - %s' % (key, value))
            curframe = inspect.currentframe()
            outerframe = inspect.getouterframes(curframe, 2)
            self[key] = value
            self._history[key] = "value=%s, file=%s, line=%s" % (
                value, outerframe[1][1], outerframe[1][2])
        super().__setattr__(key, value)

    def history(self):
        from pprint import pprint
        pprint(self._history)

if __name__ == '__main__':
    d = Trackable({
        'name': "vivek",
        'city': "Bangalore",
        'state': "Karnataka"
    })

#TODO: warning when existing value is changed.
#TODO: override update