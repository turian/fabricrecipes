from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

import fabric.network

import sys
from os.path import expanduser
from paramiko.config import SSHConfig

def disconnect_all():
    """
    disconnect from all hosts
    """
    try:
        fabric.network.disconnect_all()
    except Exception, e:
        print >> sys.stderr, type(e), e
        print >> sys.stderr, "disconnect_all() didn't work (perhaps fabric < 0.9.4, http://docs.fabfile.org/0.9.3/api/core/network.html#fabric.network.disconnect_all)"
        print >> sys.stderr, "running old-skool disconnect_all hack: http://docs.fabfile.org/0.9.3/usage/library.html?highlight=wait#disconnecting"

        from fabric.state import connections
        for key in connections.keys():
            connections[key].close()
            del connections[key]


def reboot(wait=10.):
    """
    Reboot the server, and sleep for wait seconds.
    """
    run('sudo /sbin/shutdown -r now')
    disconnect_all()

    print >> sys.stderr, "Sleeping %f seconds after reboot..." % wait
    import time
    time.sleep(wait)
    print >> sys.stderr, "...done sleeping %f seconds after reboot" % wait

def annotate_hosts_with_ssh_config_info():
    """
    Load settings from ~/.ssh/config
    NOTE: Need to define env.hosts first.
    Code from http://markpasc.typepad.com/blog/2010/04/loading-ssh-config-settings-for-fabric.html
    """
    def hostinfo(host, config):
        hive = config.lookup(host)
        if 'user' in hive:
            host = '%s@%s' % (hive['user'], host)
        if 'port' in hive:
            host = '%s:%s' % (host, hive['port'])
        return host

    try:
        config_file = file(expanduser('~/.ssh/config'))
    except IOError:
        pass
    else:
        config = SSHConfig()
        config.parse(config_file)
        keys = [config.lookup(host).get('identityfile', None)
            for host in env.hosts]
        env.key_filename = [key for key in keys if key is not None]
        env.hosts = [hostinfo(host, config) for host in env.hosts]
