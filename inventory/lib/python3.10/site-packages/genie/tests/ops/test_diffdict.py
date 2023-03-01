import unittest
from genie.ops.base.diffdict import DiffDict

class test_Diffdict(unittest.TestCase):

    def test_init(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = a

        dd = DiffDict(a,b)
        dd.d1 = a
        dd.d2 = b

    def test_same_dict(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = a

        dd = DiffDict(a,b)
        dd.findDiff()
        self.assertEqual(str(dd), '')

    def test_diff_dict(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'f':7, 'c':{'ca':8, 'cb':9}}

        dd = DiffDict(a,b)
        dd.findDiff()
        self.assertEqual(str(dd), ' +f: 7\n -b: 7')

    def test_modified_dict(self):
        a = {'a':5, 'b':7, 'c':{'cc':7, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':9}}

        dd = DiffDict(a,b)
        dd.findDiff()
        self.assertEqual(str(dd), " +c['cc']: 8\n -c['cc']: 7")

    def test_diff_dict2(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':9}}

        dd = DiffDict(a,b)
        dd.findDiff()
        self.assertEqual(str(dd), " +c['cc']: 8\n -c['ca']: 8")

    def test_diff_added(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':9}}

        dd = DiffDict(a,b)
        dd.findDiff()
        added = dd.added()
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0].path, "c['cc']")
        self.assertEqual(added[0].value, 8)
        self.assertEqual(str(added), " +c['cc']: 8")
        self.assertEqual(str(dd.modified()), "")

    def test_diff_added2(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'k':7, 'c':{'cc':8, 'cb':9}}

        dd = DiffDict(a,b)
        dd.findDiff()
        added = dd.added()
        self.assertEqual(len(added), 2)
        self.assertEqual(added[0].path, "c['cc']")
        self.assertEqual(added[0].value, 8)
        self.assertEqual(added[1].path, "k")
        self.assertEqual(added[1].value, 7)
        self.assertEqual(str(added), " +c['cc']: 8\n +k: 7")

        removed = dd.removed()
        self.assertEqual(len(removed), 2)
        self.assertEqual(str(removed), " -b: 7\n -c['ca']: 8")
        self.assertEqual(str(dd.modified()), "")

    def test_diff_removed(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':9}}

        dd = DiffDict(b,a)
        dd.findDiff()
        added = dd.added()
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0].path, "c['ca']")
        self.assertEqual(added[0].value, 8)
        self.assertEqual(str(added), " +c['ca']: 8")
        self.assertEqual(str(dd.modified()), "")

    def test_diff_removed2(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'k':7, 'c':{'cc':8, 'cb':9}}

        dd = DiffDict(b,a)
        dd.findDiff()
        added = dd.added()
        self.assertEqual(len(added), 2)
        self.assertEqual(added[1].path, "c['ca']")
        self.assertEqual(added[1].value, 8)
        self.assertEqual(added[0].path, "b")
        self.assertEqual(added[0].value, 7)
        self.assertEqual(str(added), " +b: 7\n +c['ca']: 8")

        removed = dd.removed()
        self.assertEqual(len(removed), 2)
        self.assertEqual(str(removed), " -c['cc']: 8\n -k: 7")
        self.assertEqual(str(dd.modified()), "")

    def test_diff_modified_1(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        c = {'a':5, 'b':7, 'c':{'ca':9, 'cb':9}}

        dd = DiffDict(a,c)
        dd.findDiff()

        modified = dd.modified()
        self.assertEqual(len(modified), 1)
        self.assertEqual(modified[0].new_value, 9)
        self.assertEqual(modified[0].old_value, 8)
        self.assertEqual(str(modified), " +c['ca']: 9\n -c['ca']: 8")

    def test_diff_modified(self):
        a = {'a':5, 'b':4, 'c':{'ca':8, 'cb':9}}
        c = {'a':5, 'b':7, 'c':{'ca':9, 'cb':9}}

        dd = DiffDict(a,c)
        dd.findDiff()

        modified = dd.modified()
        self.assertEqual(len(modified), 2)
        self.assertEqual(modified[1].path, "c['ca']")
        self.assertEqual(modified[1].new_value, 9)
        self.assertEqual(modified[1].old_value, 8)
        self.assertEqual(modified[0].path, "b")
        self.assertEqual(modified[0].new_value, 7)
        self.assertEqual(modified[0].old_value, 4)
        self.assertEqual(str(modified),
                         " +b: 7\n -b: 4\n +c['ca']: 9\n -c['ca']: 8")
