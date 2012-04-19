#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent remote interface to keep the set #
# of installed packages on a Debian or Ubuntu machine consistent.     #
#                                                                     #
#######################################################################
"""

from fabric.api import task, env
from fabric.colors import red, yellow, green
from config import config
import os

env.warn_only = True

# Each manifest file must be a simple text file with one package name 
# per line and Unix line-endings
MUSTHAVELATEST = "./musthavelatest"
MUSTHAVE = "./musthave"
MAYHAVE = "./mayhave"
MAYNOTHAVE = "./maynothave"

def usage():
    """ Print help text. """
    print "fab -H <host> pkgsync.sync:musthavelatest=\
        /etc/pkgsync/musthavelatest,musthave=/etc/pkgsync/musthave"

@task
def sync(musthavelatest=config.get("pkgsync", {}).get("musthavelatest", ""),
            musthave=config.get("pkgsync", {}).get("musthave", ""),
            mayhave=config.get("pkgsync", {}).get("mayhave", ""),
            maynothave=config.get("pkgsync", {}).get("maynothave", "")):
    """
    Sync a system's packages with a pre-defined manifest. 
    The ``mayhave`` list currently gets ignored.
    """
    pkgspec = {}
    if os.path.isfile(musthavelatest):
        pkgspec.update(generate_package_list(musthavelatest, "latest"))
    
    if os.path.isfile(musthave):
        pkgspec.update(generate_package_list(musthave, "installed"))
    
    if os.path.isfile(maynothave):
        pkgspec.update(generate_package_list(maynothave, "removed"))
    
    if len(pkgspec) == 0:
        print yellow("No packages specified")
        return
        
    import apt
    ok, fail = apt.ensure(**pkgspec)
    if fail == 0:
        print green("%s: %d packages sync'ed." % (env.host, ok))
    elif ok == 0:
        print red("%s: %d packages failed to sync." % (env.host, fail))
    else:
        print yellow("%s: %d packages sync'd and %d packages failed" % (env.host, ok, fail))

def generate_package_list(fn, state):
    """ Helper function to read manifests. """
    with open(fn, "rb") as fp:
        return ((pkg, state) for pkg in fp.read().split("\n"))