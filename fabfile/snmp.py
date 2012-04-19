#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent mechanism to remotely configure  #
# snmp on a host.                                                     #
#                                                                     #
#######################################################################
"""

from fabric.api import task, env, run
from fabric.colors import red

import copy

from utils import reconfigure, is_debian_or_ubuntu
from config import config
env.warn_only = True

SNMPD_CONF_PATH = "/etc/snmp/snmpd.conf"
SNMPD_PATH = "/etc/default/snmpd"

@task
def configure(**kwargs):
    """ Configure SNMP on the server. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    params = copy.copy(config['snmp'])
    params.update(kwargs)
    
    reconfigure("snmpd.conf.template", params, SNMPD_CONF_PATH)
    reconfigure("snmpd.template", params, SNMPD_PATH)


@task
def deploy():
    """ Install, configure and start snmpd. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    
    import apt, service
    packages = {"snmpd":"latest"}
    if run("cat /etc/issue").find("6.0") > -1:
        # its debian 6
        packages["snmp-mibs-downloader"] = "installed"
        
    apt.ensure(**packages)
    
    configure()
    service.ensure(snmpd="restarted")