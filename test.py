
import unittest
import cloudpush
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
        self.container_path = path.abspath(path.join(gettempprefix(), self.container_name))
        copytree('testfixtures', self.container_path)
        self.client = cloudpush.CloudFilesClient(config, self.container_path)

    def tearDown(self):
        rmtree(self.container_path)
        self.container_name = None
        self.container_path = None

    def testCloudPush(self):
        self.client.attach()
        try:
            self.client.url()
        except cloudpush.ContainerNotPublic:
            pass
        else:
            self.fail('Should throw ContainerNotPublic')

        url = self.client.publish()
        assert url, 'URL should not be empty'

        #self.client.push(['file.txt'])
        self.client.push()
        print self.client.url(['file.txt'])

        # Detach
        self.client.detach()

        try:
            self.client.detach()
        except cloudpush.NotAttached:
            pass
        else:
            self.fail('Should throw NotAttached')



if __name__ == '__main__':
    unittest.main()

