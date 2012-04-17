#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent mechanism to remotely configure  #
# cups on a host.                                                     #
#                                                                     #
#######################################################################
"""

from fabric.api import task, env
from fabric.colors import red
from utils import reconfigure, is_debian_or_ubuntu
from config import CUPS_SERVER

env.warn_only = True

CUPS_CONF_PATH = "/etc/cups/client.conf"

@task
def config(server=env.get("CUPS_SERVER", CUPS_SERVER)):
    """ Configure NTP sync to server. """
    
    # Upload configuration
    reconfigure("cups_client.conf.template", {"server":server}, CUPS_CONF_PATH)

@task
def deploy():
    """ Install and configure and start cups client. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    
    import apt, service
    packages = {"cupsys":"latest", "cups-client":"latest"}
    apt.ensure(**packages)
    config()
    service.ensure(cupsys="restarted")
