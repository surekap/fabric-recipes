#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent mechanism to remotely configure  #
# ntp sync to a server on a host.                                     #
#                                                                     #
#######################################################################
"""

from fabric.api import task, run, env
from fabric.colors import red
from utils import reconfigure, is_debian_or_ubuntu
env.warn_only = True

from config import TIME_SERVER, TIMEZONE

NTP_CONF_PATH = "/etc/ntp.conf"

@task
def timezone(timezone=env.get("TIMEZONE", TIMEZONE)):
    """ Set the timezone. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    
    import apt
    apt.ensure(tzdata="latest")
    return run("cp -f /usr/share/zoneinfo/%s /etc/localtime" % timezone)

@task
def config():
    """ Configure NTP sync to server. """
    
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    
    # Upload configuration
    reconfigure("ntp_client.conf.template", locals(), NTP_CONF_PATH)

@task
def deploy(server=env.get("TIME_SERVER", TIME_SERVER)):
    """ Install, configure and start ntp sync and timezone. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
        
    import apt, service
    packages = {"ntp":"latest", "ntp-simple":"latest", "ntpdate":"latest"}
    apt.ensure(**packages)
    config()
    
    # Sync with server
    run("ntpdate %s" % server)
    
    # Sync hardware clock to correct time
    run("hwclock --systohc")
    
    service.ensure(ntp="restarted")
    timezone()

@task
def status():
    """ List the servers with which the host is synchronized. """
    print run("ntpq")
    print run("ntpdc -p")