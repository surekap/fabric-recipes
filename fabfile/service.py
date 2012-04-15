#!/bin/env python

"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent remote interface to control      #
# services on debian.                                                 #
#                                                                     #
#######################################################################
"""

from fabric.api import task, sudo, run, env
from fabric.contrib.files import exists
from fabric.colors import red, green, yellow
import sys

env.warn_only = True
VALID_STATES = ('running', 'started', 'stopped', 'restarted')

SERVICE_PATH = "/usr/sbin/service"

def usage():
    """Print the help text
    """
    print """fab service.ensure:[pkgspec1]=[state],[pkgspec2]=[state]\n
state := running|started|stopped|restarted
    """

SERVICE_STATUS_RUNNING = 1
SERVICE_STATUS_NOTRUNNING = 0
SERVICE_STATUS_NOEXIST = -1

def service_get_status(service):
    svcstatus = run("service %s status" % service)
    if svcstatus.find("unrecognized") > -1:
        return SERVICE_STATUS_NOEXIST
    elif svcstatus.find("not running") > -1:
        return SERVICE_STATUS_NOTRUNNING
    elif svcstatus.find("running") > -1:
        return SERVICE_STATUS_RUNNING
    elif svcservice == "iptables" and svcstatus.find("ACCEPT") != -1:
        return SERVICE_STATUS_RUNNING
    
    return SERVICE_STATUS_NOTRUNNING

def service_stop(service):
    svcstatus = run("service %s stop" % service)
    return svcstatus

def service_start(service):
    svcstatus = run("service %s start" % service)
    return svcstatus

def service_restart(service):
    svcstatus = run("service %s restart" % service)
    if svcstatus.failed:
        svcstatus = service_stop(service)
        svcstatus = service_start(service)
    return svcstatus

def init_get_status(service):
    if not exists("/etc/init.d/%s" % service):
        return SERVICE_STATUS_NOEXIST
    
    svcstatus = run("/etc/init.d/%s status" % service)
    
    if svcstatus.find("not running") > -1:
        return SERVICE_STATUS_NOTRUNNING
    elif svcstatus.find("running") > -1:
        return SERVICE_STATUS_RUNNING
    
    return SERVICE_STATUS_NOTRUNNING

def init_start(service):
    svcstatus = run("/etc/init.d/%s start" % service)
    return svcstatus

def init_stop(service):
    svcstatus = run("/etc/init.d/%s stop" % service)
    return svcstatus

def init_restart(service):
    svcstatus = run("/etc/init.d/%s restart" % service)
    if svcstatus.failed:
        svcstatus = init_stop(service)
        svcstatus = init_start(service)
    return svcstatus
    
def _get_functions():
    if exists(SERVICE_PATH):
        return {
            "get_status": service_get_status,
            "start": service_start,
            "stop": service_stop,
            "restart": service_restart
        }
    else:
        return {
            "get_status": init_get_status,
            "start": init_start,
            "stop": init_stop,
            "restart": init_restart
        }

@task
def ensure(**kwargs):
    """ Ensure that the list of services are (running|started|stopped|restarted)"""
    function_lib = _get_functions()
    for service, state in kwargs.iteritems():
        if state not in VALID_STATES:
            print "Invalid state for %s: %r" % (service, state)
            print usage()
            sys.exit(1)
        
        running = function_lib['get_status'](service)
        
        if running == SERVICE_STATUS_NOEXIST:
            print "Cannot control nonexistent service: %s" % service
            continue
            
        if running == SERVICE_STATUS_NOTRUNNING and state in ("started", "running"):
            function_lib['start'](service)
        elif running == SERVICE_STATUS_RUNNING and state == "stopped":
            function_lib['stop'](service)
        elif state == "restarted":
            function_lib['restart'](service)
    
@task
def status(service):
    """ Get the status of a service. """
    function_lib = _get_functions()
    s = function_lib['get_status'](service)
    print "%s: " % service,
    if s is SERVICE_STATUS_RUNNING:
        green("running")
    elif s is SERVICE_STATUS_NOTRUNNING:
        yellow("not running")
    elif s is SERVICE_STATUS_NOEXIST:
        red("no exist")
    return s

