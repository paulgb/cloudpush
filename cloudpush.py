
import cloudfiles
import argparse
from os import environ, path
import json

COMMANDS = ('info', 'attach', 'url', 'publish')
OPTS = ('username', 'api_key', 'cache_timeout', 'authurl', 'friendly')

CONFIG_FILE = '.cloudpush'
BASE_CONFIG_FILE = path.expanduser(path.join('~', CONFIG_FILE))
DEFAULT_CACHE_TIMEOUT = 10 * 60
DEFAULT_AUTH_URL = cloudfiles.us_authurl

class CloudFilesClient(object):
    _conn = None
    _config = None

    def __init__(self, opts):
        try:
            self.username = opts['username']
            self.api_key = opts['api_key']
        except KeyError:
            print 'bad'
            exit()
        self.cache_timeout = opts.get('cache_timeout', DEFAULT_CACHE_TIMEOUT)
        self.auth_url = opts.get('api_key', DEFAULT_AUTH_URL)

    @property
    def connection(self):
        if not self._conn:
            self._conn = cloudfiles.get_connection(self.username, self.api_key)
        return self._conn

    @property
    def config(self):
        if self._config is None:
            try:
                self._config = json.load(file(CONFIG_FILE))
            except IOError:
                self._config = {}
        return self._config

    def url(self, args):
        config = self.config
        container = self.config['container']
        try:
            print self.connection[container].public_uri()
        except cloudfiles.errors.ContainerNotPublic:
            print 'not public'

    def attach(self, args):
        config = self.config
        
        if 'container' in config:
            print 'Already attached to %s' % config['container']
            if args['container']:
                raise NotImplementedError()
            container_name = config['container']
        elif args['container']:
            container_name = args['container']
        else:
            parent_dir, container_name = path.split(path.realpath('.'))
        config['container'] = container_name
        print config

        fh = file(CONFIG_FILE, 'w')
        json.dump(config, fh)

        try:
            self.connection.create_container(config['container'], True)
        except cloudfiles.errors.ContainerExists:
            print 'Container already exists'

    def publish(self, args):
        config = self.config
        connection = self.connection
        container = config['container']

        connection[container].make_public(ttl=self.cache_timeout)
        self.url(args)

    def info(self, args):
        connection = self.connection
        print 'Listing Containers:'
        for container in connection.list_containers_info():
            print container['name']
            print '    %s objects' % container['count']
            if args['friendly']:
                print '    %s' % friendly_size(container['bytes'])
            else:
                print '    %s' % container['bytes']

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
    return dict((k,v) for k,v in opts.items() if k in OPTS and v is not None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('--friendly', '-f', action='store_true',
            help='Human-friendly file sizes')
    parser.add_argument('--container', '-c')

    args = vars(parser.parse_args())

    client_opts = clean_opts(environ)

    try:
        config = json.load(file(BASE_CONFIG_FILE))
    except IOError:
        pass
    else:
        client_opts.update(clean_opts(config))

    client_opts.update(clean_opts(args))
    
    client = CloudFilesClient(client_opts)
    getattr(client, args['command'])(args)


if __name__ == '__main__':
    main()

