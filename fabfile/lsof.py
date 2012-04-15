#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an query mechanism to check open ports on a    #
# remote host.                                                        #
#                                                                     #
#######################################################################
"""

from fabric.api import task, run

@task
def tcp():
    """ List open tcp connections """
    print run("lsof -i tcp")

@task
def udp():
    """ List open udp connections """
    print run("lsof -i udp")

@task
def net():
    """ List open tcp and udp connections """
    print run("lsof -i tcp -i udp")