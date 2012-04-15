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
import sys

env.warn_only = True

APT_PATH = "/usr/bin/apt-get"
APT = "DEBIAN_PRIORITY=critical %s" % APT_PATH

def usage():
    """Print the help string"""
    print "fab apt.ensure:[pkgspec]=[installed|latest|removed],purge=[True|False]"

@task
def status(pkgspec):
    """Get the status of a package as a tuple (installed, upgradeable) 
    given a package-name.
    """
    cmd = "apt-show-versions -v -p %s"
    pkgstatus = run(cmd % pkgspec)
    return (not (pkgstatus.find("not installed") > -1), (pkgstatus.find("upgradeable") > -1))

def install(pkgspec, upgrade=False):
    """Install a package."""
    (installed, upgradable) = status(pkgspec)
    if (not installed) or (upgrade and upgradable):
        cmd = "%s -q -y install '%s'" % (APT, pkgspec)
        ret = run(cmd)
        if ret.failed:
            print "'apt-get install %s' failed: %s" % (pkgspec, ret)
        return True
    else:
        return False

def remove(pkgspec, purge=False):
    """Remove a package."""
    (installed, upgradable) = status(pkgspec)
    if not installed:
        return False
    else:
        purge = "--purge" if purge else ''
        cmd = "%s -q -y %s remove '%s'" % (APT, purge, pkgspec)
        ret = run(cmd)
        if ret.failed:
            print "'apt-get remove %s' failed: %s" % (pkgspec, ret)
        return True

@task
def ensure(**kwargs):
    """Idempotent operation to ensure state of a package."""
    purge = False
    if "purge" in kwargs:
        purge = kwargs.pop("purge")
    
    for package, state in kwargs.iteritems():
        if state not in ("installed", "latest", "removed"):
            usage()
            sys.exit(1)
        
        if state == "latest":
            install(package, upgrade=True)
        elif state == "installed":
            install(package)
        elif state == "removed":
            remove(package, purge=purge)