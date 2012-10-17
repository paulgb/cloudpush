
import unittest
from cloudpush import CloudFilesClient
from random import choice
from shutil import copytree, rmtree
from os import path
import string
from tempfile import gettempprefix
import json

class CloudFilesTest(unittest.TestCase):
    def random_container_name(self):
        return ''.join(choice(string.ascii_letters) for x in xrange(0, 10))

    def setUp(self):
        config = json.load(file('testconfig.json'))
        self.container_name = self.random_container_name()
        self.container_path = path.join(gettempprefix(), self.container_name)
        copytree('testfixtures', self.container_path)
        print self.container_path
        self.client = CloudFilesClient(config)

    def tearDown(self):
        rmtree(self.container_path)
        self.container_name = None
        self.container_path = None

    def testAttach(self):
        pass


if __name__ == '__main__':
    unittest.main()

