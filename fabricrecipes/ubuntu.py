"""
Ubuntu fabric recipes.
"""
from fabric.api import *

def aptdistupgrade():
    run('sudo apt-get update')
    run('sudo apt-get dist-upgrade -y')
