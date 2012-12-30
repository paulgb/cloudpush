CloudPush
=========

CloudPush is a command-line tool for managing static websites hosted on [Rackspace Cloud Files](http://www.rackspace.com/cloud/public/files/) or another [Open Stack Swift](http://swift.openstack.org)-powered service.

Installation
------------

Configuration
-------------

CloudPush can be configured in one of two ways. In both cases the configurable variables are the same:

* `username`: your username
* `api_key`: your API key
* `cache_timeout`: amount of time files live in the CDN, in seconds
* `authurl`: the authorization URL (defaults to Cloud Files US, you only need to change this if you use Cloud Files UK or another Swift server.)

### File-based Configuration

Configuraition m be provided by a file called `.cloudpush` in the user's home directory.

An example file looks like this:

    {
        "username": "<your username>",
        "api_key": "<your api key>"
    }

### Environment-based configuration

CloudPush will also look through the environment for configuraiton settings. The environment variables are uppercase and prefixed with `CLOUDFILES_`.

    export CLOUDFILES_USERNAME=<your username>
    export CLOUDFILES_API_KEY=<your api key>


Usage
-----

### Attach

CloudPush works by attaching a directory to a Swift container. The first time you run CloudPush in a directory, you must run `cloudpush attach` to create a container and attach it to the current directory.

### Push

To push local files to the server, run `cloudpush push [filename...]`. This pushes the named files (and, recursively, directories) to the server. If no filename is given, the whole directory will be pushed.

Files are hashed and compared with the server, so only files that differ from the version on the server will be pushed. Note that last modified dates are not compared and the synchronization is only one-way.

### Publish

After attaching a directory, you can make the contents of the container public by running `cloudpush publish`. If successful, the base URL of the directory will be returned.

### Detach

To detach a container from the current directory, *and delete the container*, run `cloudpush detach`. This recursively deletes all the files from the container, deletes the container, and then detaches the container from the directory.

### Info

CloudPush also has an info command (`cloudpush info`) which returns some values related to the currently attached container. This includes the CDN url (if public) and a token that can be used to manually make `REST` API calls to the server.

A note on CDN hosting
---------------------

When using public files on Rackspace Cloud Files, the files are served through a Content Delivery Network (CDN). As a result, changes you make may not appear immediately. When in doubt, use the [Rackspace Cloud](https://mycloud.rackspace.com) interface to see if changes have been applied to the master version.

