#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent mechanism to remotely set a      #
# machine's locale.                                                   #
#                                                                     #
#######################################################################
"""
from fabric.api import env, run, task
from utils import reconfigure
env.warn_only = True

@task
def configure():
    """ Set the locale to be:
        en_IN UTF-8
        en_US ISO-8859-1
        en_US.UTF-8 UTF-8
    """
    reconfigure("locale.template", {}, "/etc/locale.gen")
    run("/usr/sbin/locale-gen")

