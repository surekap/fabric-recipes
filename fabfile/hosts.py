#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent mechanism to remotely set a      #
# machine's hostname and domainname.                                  #
#                                                                     #
#######################################################################
"""

from fabric.api import task, env, run
from utils import is_debian_or_ubuntu
env.warn_only = True

@task
def ensure(**kwargs):
    """ Ensure that the hostname for each host is set correctly according to parameters. """
    if env.host in kwargs:
        if is_debian_or_ubuntu():
            run("""echo "%s" > /etc/hostname""" % kwargs[env.host])
            run("""sysctl kernel.hostname=%s""" % kwargs[env.host])
            
            import service
            svc = {"hostname.sh":"restarted"}
            service.ensure(**svc)
        
    
@task
def ensure_from_file():
    """ Use the file to set hostnames """
    pass