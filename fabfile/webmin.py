#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an mechanism to remotely deploy and configure  #
# webmin on a host.                                                   #
#                                                                     #
#######################################################################
"""

from fabric.api import task, env, run, cd
from fabric.contrib.files import exists
from fabric.colors import red
import utils

import apt, service

env.warn_only = True

BASE = "webmin_1.580_all.deb"
BASE_MD5 = "093c720a988125a536fa9fda16080fe6"
URL = "http://prdownloads.sourceforge.net/webadmin/"
ARCHIVE = "/root/" + BASE
INSTALLED = "/etc/webmin/version"

RESUME_ATTEMPT = 1

def download():
    """ Download webmin """
    global RESUME_ATTEMPT
    while True:
        with cd("/root"):
            run("wget -c %s%s" % (URL, BASE))
        if verify():
            return True
        else:
            if RESUME_ATTEMPT == 0:
                run("rm %s" % BASE)
            elif RESUME_ATTEMPT < 0:
                raise SystemExit("Unable to download %s" % BASE)
            RESUME_ATTEMPT -= 1

def verify():
    """ Verify the downloaded package """
    if not exists(ARCHIVE):
        return False
    code = run("md5sum %s" % ARCHIVE)
    return code.find(BASE_MD5) > -1
    

def install():
    """ Install the package. """
    with cd("/root"):
        run("dpkg -i %s" % ARCHIVE)
        version = run("cat %s" % INSTALLED)
        if version.strip() != "1.580":
            return False
    return True

@task
def deploy():
    """ Install, configure and start webmin. """
    
    if not utils.is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
        
    # Check if webmin is installed
    installed, upgradeable = apt.status("webmin")
    if not installed:
        packages = {
            "libnet-ssleay-perl":"latest",
            "libauthen-pam-perl":"latest",
            "libio-pty-perl":"latest",
            "libmd5-perl":"latest"
        }
        apt.ensure(**packages)
        download()
        install()
    
    service.ensure(webmin="running")