
import unittest
from cloudpush import cloudpush
from random import choice
from shutil import copytree, rmtree
from os import path
import string
from tempfile import gettempprefix
import json
from urlparse import urlparse

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

        res = self.client.push(['file.txt'])

        self.assertEquals({'skipped': 0, 'synced': 1, 'total': 1}, res)

        res = self.client.push()
        
        self.assertEquals({'skipped': 1, 'synced': 2, 'total': 3}, res)

        res = self.client.push()

        self.assertEquals({'skipped': 3, 'synced': 0, 'total': 3}, res)

        res = self.client.url(['file.txt'])
        self.assertEquals('/file.txt', urlparse(res).path)

        res = self.client.url(['some_dir'])
        self.assertEquals('/some_dir', urlparse(res).path)

        res = self.client.url(['some_dir/test.html'])
        self.assertEquals('/some_dir/test.html', urlparse(res).path)

        self.client.detach()

        try:
            self.client.detach()
        except cloudpush.NotAttached:
            pass
        else:
            self.fail('Should throw NotAttached')



if __name__ == '__main__':
    unittest.main()

