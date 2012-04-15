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

from fabric.api import task, env
from fabric.colors import red
from utils import reconfigure, is_debian_or_ubuntu
env.warn_only = True

from config import SNMP_PUBLIC, SNMP_LOCATION, SNMP_CONTACT, SNMP_NET

SNMPD_CONF_PATH = "/etc/snmp/snmpd.conf"
SNMPD_PATH = "/etc/default/snmpd"

@task
def config(public=env.get("SNMP_PUBLIC", SNMP_PUBLIC), 
            location=env.get("SNMP_LOCATION", SNMP_LOCATION), 
            contact=env.get("SNMP_CONTACT", SNMP_CONTACT), 
            net=env.get("SNMP_NET", SNMP_NET)):
    """ Configure SNMP on the server. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    params = {
        public: public,
        location: location,
        contact: contact,
        net: net
    }
    reconfigure("snmpd.conf.template", params, SNMPD_CONF_PATH)
    reconfigure("snmpd.template", params, SNMPD_PATH)


@task
def deploy():
    """ Install, configure and start snmpd. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    
    import apt, service
    apt.ensure(snmpd="latest")
    config()
    service.ensure(snmpd="restarted")