from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

import fabric.network

import sys
import re
import string
from os.path import expanduser, join
from paramiko.config import SSHConfig

def python_major_version():
    """
    Get the Python major version number
    """
    pystr = run("python -c 'import platform; print platform.python_version()'")
    pyre = re.compile("([0-9]+\.[0-9]+)\.[0-9]+")
    assert pyre.match(pystr)
    PYTHONMAJORVERSION = pyre.match(pystr).group(1)
    print >> sys.stderr, "Remote PYTHONMAJORVERSION = %s" % PYTHONMAJORVERSION
    return PYTHONMAJORVERSION

def perl_version():
    """
    Get the Perl version number
    """
    PERLVERSION = string.strip(run("perl -v | awk '/This/ {print $4}' | sed -e 's/v//'"))
    print >> sys.stderr, "Remote PERLVERSION = %s" % PERLVERSION
    return PERLVERSION

def install_pip():
    sudo("easy_install -U pip")

def install_python_package_with_pip(package, prefix):
    # TODO: Use pip-install alias
    PIPINSTALL = 'pip install -U --src=%s --install-option="--prefix=%s"' % (join(prefix, "src"), prefix)
    run("%s %s" % (PIPINSTALL, prefix))

def install_python_github_package_with_pip(package, prefix):
    # TODO: Use pip-install alias
    PIPINSTALL = 'pip install -U --src=%s --install-option="--prefix=%s" -e' % (join(prefix, "src"), prefix)
    run("%s %s" % (PIPINSTALL, prefix))

def install_python_package_with_easy_install(package, prefix):
    # TODO: Use pip-install alias
    EASYINSTALL = 'easy_install -U --prefix=%s' % prefix
    run("%s jinja2" % EASYINSTALL)

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


def reboot(wait=20.):
    """
    Reboot the server, and sleep for wait seconds.
    You can also try fabric.operations.reboot() (http://docs.fabfile.org/0.9.3/api/core/operations.html#fabric.operations.reboot)
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

def sshagent_run(cmd):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.
    
    Note:: Fabric (and paramiko) can't forward your SSH agent. 
    This helper uses your system's ssh to do so.

    Code from: http://lincolnloop.com/blog/2009/sep/22/easy-fabric-deployment-part-1-gitmercurial-and-ssh/
    """

    for h in env.hosts:
        try:
            # catch the port number to pass to ssh
            host, port = h.split(':')
            local('ssh -p %s -A %s "%s"' % (port, host, cmd))
        except ValueError:
            local('ssh -A %s "%s"' % (h, cmd))
