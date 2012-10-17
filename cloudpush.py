
import cloudfiles
import argparse
from os import environ, path, walk, chdir
import json
from cloudfiles.errors import ContainerNotPublic
from StringIO import StringIO
from hashlib import md5

COMMANDS = ('info', 'attach', 'url', 'publish', 'push')
CONF_OPTS = ('username', 'api_key', 'cache_timeout', 'authurl')
MD5_BLOCKSIZE = 128

CONFIG_FILE = '.cloudpush'
BASE_CONFIG_FILE = path.expanduser(path.join('~', CONFIG_FILE))
DEFAULT_CACHE_TIMEOUT = 10 * 60
DEFAULT_AUTH_URL = cloudfiles.us_authurl

def all_files(base):
    for dirname, dirs, files in walk(base):
        for filename in files:
            if filename[0] != '.':
                yield path.relpath(path.join(dirname, filename))

def md5_file(filename):
    hash = md5()
    fh = file(filename)
    while True:
        chunk = fh.read(MD5_BLOCKSIZE * 128)
        if len(chunk) == 0:
            break
        hash.update(chunk)
    return hash.hexdigest()

class NotAttached(Exception):
    def __str__(self):
        print 'not attached'

class InvalidConfigurationError(Exception):
    def __str__(self):
        print 'invalid configuration'

class CloudFilesClient(object):
    _conn = None
    _site_config = None

    def __init__(self, config, sitedir='.'):
        chdir(sitedir)
        try:
            self.username = config['username']
            self.api_key = config['api_key']
        except KeyError:
            raise InvalidConfigurationError()
        self.cache_timeout = config.get('cache_timeout', DEFAULT_CACHE_TIMEOUT)
        self.auth_url = config.get('api_key', DEFAULT_AUTH_URL)

    @property
    def connection(self):
        if not self._conn:
            self._conn = cloudfiles.get_connection(self.username, self.api_key)
        return self._conn

    @property
    def site_config(self):
        if self._site_config is None:
            try:
                self._site_config = json.load(file(CONFIG_FILE))
            except IOError:
                self._site_config = {}
        return self._site_config

    def save_site_config(self):
        fh = file(CONFIG_FILE, 'w')
        json.dump(self.site_config, fh)
        fh.close()

    @property
    def container(self):
        return self.connection[self.container_name]

    @property
    def container_name(self):
        try:
            return self.site_config['container']
        except KeyError:
            raise NotAttached()

    def url(self, files=['.']):
        filename, = files
        try:
            if path.isdir(filename):
                if filename == '.':
                    return self.container.public_uri()
                else:
                    return path.join(self.container.public_uri(), filename)
            else:
                return self.container[filename].public_uri()
        except ContainerNotPublic:
            raise

    def push(self, files=['.']):
        skipped = 0
        synced = 0
        container = self.container
        objects = dict((v['name'], v) for v in container.list_objects_info())
        for push_path in files:
            if path.isdir(push_path):
                push_files = all_files(push_path)
            else:
                push_files = [push_path]

            for filename in push_files:
                if filename in objects:
                    remote_hash = objects[filename]['hash']
                    local_hash = md5_file(filename)
                    if local_hash == remote_hash:
                        skipped += 1
                        continue

                synced += 1
                ob = container.create_object(filename)
                ob.load_from_filename(filename)
        return {'skipped': skipped, 'synced': synced, 'total': skipped+synced}
         
    def detach(self):
        site_config = self.site_config
        container = self.container
        for obj in container.list_objects():
            container.delete_object(obj)
        self.connection.delete_container(self.container_name)
        del site_config['container']
        self.save_site_config()

    def attach(self, container=None):
        site_config = self.site_config
        
        if 'container' in site_config:
            print 'Already attached to %s' % site_config['container']
            if container:
                raise NotImplementedError()
            container_name = site_config['container']
        elif container:
            container_name = container
        else:
            parent_dir, container_name = path.split(path.realpath('.'))
        site_config['container'] = container_name
        self.save_site_config()

        try:
            self.connection.create_container(site_config['container'], True)
        except cloudfiles.errors.ContainerExists:
            print 'Container %s already exists' % site_config['container']

    def publish(self):
        container = self.container

        container.make_public(ttl=self.cache_timeout)
        return self.url()

    def info(self, friendly=False):
        connection = self.connection
        out = StringIO()
        for container in connection.list_containers_info():
            print >> out, container['name']
            print >> out, '    %s objects' % container['count']
            if friendly:
                print >> out, '    %s' % friendly_size(container['bytes'])
            else:
                print >> out, '    %s' % container['bytes']
        return out


def friendly_size(size):
    r'''
        >>> friendly_size(1024)
        '1.0 KB'
        >>> friendly_size(128)
        '128.0 bytes'
        >>> friendly_size(1024 * 8.3)
        '8.3 KB'
        >>> friendly_size(1024 * 1024 * 5.5)
        '5.5 MB'
    '''
    for unit in ['bytes','KB','MB','GB','TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, unit)
        size /= 1024.0


def clean_opts(opts):
    r'''
        >>> clean_opts({'username': 'baz', 'foo': 'bar'})
        {'username': 'baz'}
    '''
    return dict((k,v) for k,v in opts.items() if k in CONF_OPTS and v is not None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('--friendly', '-f', action='store_const', const=True,
            help='Human-friendly file sizes')
    parser.add_argument('--container', '-c')
    parser.add_argument('files', nargs='*')

    args = vars(parser.parse_args())

    client_opts = clean_opts(environ)

    try:
        config = json.load(file(BASE_CONFIG_FILE))
    except IOError:
        pass
    else:
        client_opts.update(clean_opts(config))

    for opt in CONF_OPTS:
        try:
            val = args.pop(opt)
        except KeyError:
            pass
        else:
            if val is not None:
                conf[opt] = val
    
    client = CloudFilesClient(client_opts)
    command_fun = getattr(client, args.pop('command'))
    args = dict((k,v) for k,v in args.items() if v not in (None, []))

    print command_fun(**args)


if __name__ == '__main__':
    main()

