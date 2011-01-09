"""
Ubuntu fabric recipes.
"""
from fabric.api import *

import string

def aptdistupgrade():
    run('sudo apt-get update')
    run('sudo apt-get dist-upgrade -y')

def ubuntuversion():
    return string.strip(run('lsb_release -sr'))

def mongoubuntuversion():
    return ubuntuversion().replace(".0", ".")
