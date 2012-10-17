
import cloudfiles
import argparse
from os import environ, path
import json

COMMANDS = ('info', 'attach', 'url', 'publish', 'push')
CONF_OPTS = ('username', 'api_key', 'cache_timeout', 'authurl')

CONFIG_FILE = '.cloudpush'
BASE_CONFIG_FILE = path.expanduser(path.join('~', CONFIG_FILE))
DEFAULT_CACHE_TIMEOUT = 10 * 60
DEFAULT_AUTH_URL = cloudfiles.us_authurl

class CloudFilesClient(object):
    _conn = None

    def __init__(self, config):
        try:
            self.username = config['username']
            self.api_key = config['api_key']
        except KeyError:
            print 'bad'
            exit()
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
        pass

    @property
    def container(self):
        return self.connection[self.site_config['container']]

    def url(self):
        try:
            print self.container.public_uri()
        except cloudfiles.errors.ContainerNotPublic:
            print 'not public'

    def push(self):
        container = self.container
        files = args['files']
        for filename in files:
            print filename
            ob = container.create_object(filename)
            ob.load_from_filename(filename)
         
    def attach(self):
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

    def publish(self):
        config = self.config
        connection = self.connection
        container = config['container']

        connection[container].make_public(ttl=self.cache_timeout)
        self.url(args)

    def info(self, friendly=False):
        connection = self.connection
        print 'Listing Containers:'
        for container in connection.list_containers_info():
            print container['name']
            print '    %s objects' % container['count']
            if friendly:
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

    print args
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

    command_fun(**args)


if __name__ == '__main__':
    main()

