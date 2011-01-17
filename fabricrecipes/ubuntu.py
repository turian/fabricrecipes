"""
Ubuntu fabric recipes.
"""
from fabric.api import *

import string

def aptdistupgrade():
    sudo('apt-get update')
    sudo('apt-get dist-upgrade -y')

def ubuntuversion():
    return string.strip(run('lsb_release -sr'))

def ubuntucodename():
    return string.strip(run('lsb_release -sc'))

def enable_multiverse():
    UBUNTUCODENAME = ubuntucodename()
    sudo('echo "deb http://us.archive.ubuntu.com/ubuntu/ %s multiverse" >> /etc/apt/sources.list' % UBUNTUCODENAME)
    sudo('echo "deb-src http://us.archive.ubuntu.com/ubuntu/ %s multiverse" >> /etc/apt/sources.list' % UBUNTUCODENAME)
    sudo('echo "deb http://us.archive.ubuntu.com/ubuntu/ %s-updates multiverse" >> /etc/apt/sources.list' % UBUNTUCODENAME)
    sudo('echo "deb-src http://us.archive.ubuntu.com/ubuntu/ %s-updates multiverse" >> /etc/apt/sources.list' % UBUNTUCODENAME)

def mongoubuntuversion():
    return ubuntuversion().replace(".0", ".")
