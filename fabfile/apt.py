#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent remote interface to debian's apt #
# package manager.                                                    #
#                                                                     #
#######################################################################
"""

from fabric.api import task, run, env
from fabric.colors import red, yellow
from utils import reconfigure
from config import config
import sys

env.warn_only = True

APT_PATH = "/usr/bin/apt-get"
APT = "DEBIAN_PRIORITY=critical %s" % APT_PATH

APT_SOURCES_PATH = "/etc/apt/sources.list"

APT_PROXY_PATH = "/etc/apt/apt.conf.d/02proxy"
APT_PROXY_SERVER = "192.168.0.6"
APT_PROXY_PORT = "3142"

def usage():
    """Print the help string"""
    print "fab apt.deploy:server=[apt-proxy-server],port=[apt-proxy-port]"
    print "fab apt.ensure:[pkgspec]=[installed|latest|removed],purge=[True|False]"
    print "fab apt.status:[pkgspec],[pkgspec],[pkgspec]"
    print "fab apt.cleaned"
    

def full_status(pkgspec):
    """Get the status of a package as a tuple (installed, upgradeable) 
    given a package-name.
    """
    cmd = "apt-show-versions -v -p %s"
    pkgstatus = run(cmd % pkgspec)
    if pkgstatus.failed:
        print red("Unable to query package status: %s" % pkgspec)
    return (not (pkgstatus.find("not installed") > -1), (pkgstatus.find("upgradeable") > -1))

@task
def status(pkgspec):
    """Get the status of a package (installed=True, uninstalled=False) 
    given a package-name.
    """
    cmd = "dpkg -s %s"
    pkgstatus = run(cmd % pkgspec)
    if pkgstatus.find("install ok installed") > -1:
        return True
    return False

def install(pkgspec, upgrade=False, force=False):
    """Install a package."""
    if upgrade == False:
        (installed, upgradable) = status(pkgspec), False
    else:
        (installed, upgradable) = full_status(pkgspec)
    
    force = "--force-yes" if force is True else ""
    if (not installed) or (upgrade and upgradable):
        cmd = "%s -q -y %s install '%s'" % (APT, force, pkgspec)
        ret = run(cmd)
        if ret.failed:
            print red("'apt-get install %s' failed: %s" % (pkgspec, ret))
            return False
    return True

def remove(pkgspec, purge=False):
    """Remove a package."""
    installed = status(pkgspec)
    if not installed:
        return True
    else:
        purge = "--purge" if purge else ''
        cmd = "%s -q -y %s remove '%s'" % (APT, purge, pkgspec)
        ret = run(cmd)
        if ret.failed:
            print red("'apt-get remove %s' failed: %s" % (pkgspec, ret))
            return False
        return True

@task
def ensure(**kwargs):
    """Idempotent operation to ensure state of a package."""
    purge = False
    if "purge" in kwargs:
        purge = kwargs.pop("purge")
    
    ok = fail = 0
    for package, state in kwargs.iteritems():
        if state not in ("installed", "latest", "removed"):
            usage()
            sys.exit(1)
        
        result = False
        if state == "latest":
            result = install(package, upgrade=True, force=True)
        elif state == "installed":
            result = install(package, force=True)
        elif state == "removed":
            result = remove(package, purge=purge)
        
        if result is False:
            fail += 1
        else:
            ok += 1
    return ok, fail
    
@task
def cleaned():
    """ Clean up and update the apt cache on each host."""
    run("apt-get update")
    run("apt-get autoclean")

@task
def deploy(server=config.get("apt", {}).get("apt_proxy_server", ""), port=config.get("apt", {}).get("apt_proxy_port", "")):
    """ Direct each host to use an apt proxy (approx/apt-proxy/apt-cacher-ng). """
    
    params = {'server':server, 'port':port}
    reconfigure("apt_02proxy.template", params, APT_PROXY_PATH)
    
    # Only copy sources.list if we are using debian 6.0
    if run("cat /etc/issue").find("6.0") > -1:
        # its debian 6
        reconfigure("apt_sources.list6.0.template", {}, APT_SOURCES_PATH)
        print yellow("Debian 6.0 found - standardizing %s" % APT_SOURCES_PATH)
    
    run("apt-get update")

