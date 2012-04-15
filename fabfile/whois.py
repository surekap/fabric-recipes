#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an query mechanism to get info on a host by ip #
# or by MAC address.                                                  #
#                                                                     #
#######################################################################
"""

from fabric.api import task, run, env, roles, hide
from fabric.colors import red, green, yellow
import sys, re

env.warn_only = True

def usage():
    """ Print help string """
    print "fab whois.ip:192.168.0.99,192.168.0.100"
    print "fab whois.mac:001b11166bfe,70cd60ffe401"
    sys.exit(1)


def get_db():
    with hide("running", "stdout", "stderr"):
        ethdb = run("cat /var/lib/iptraf/ethernet.desc")
        arpdb = run("arp -a -n")
    
    ethdb = [r.split(":") for r in ethdb.split("\n")]   # MAC -> host
    ethdb = [(r[0].upper(), r[1]) for r in ethdb]
    arpdb = [re.search("\((.*)\).* at (.*) \[.*", r).groups() for r in arpdb.split("\n")]   # IP -> MAC
    arpdb = [(r[0], r[1].replace(":", "")) for r in arpdb]
    return ethdb, arpdb

@roles('firewall')
@task
def ip(*args):
    """ Find machine name by ip """
    if len(args) < 1:
        usage()
    ethdb, arpdb = get_db()
    for ip in args:
        record = [r for r in arpdb if r[0] == ip]
        if len(record) == 0:
            print yellow("Unable to get MAC address of ip: %s. Please try with MAC address if you have it." % ip)
            continue
        else:
            mac = record[0][1]
            record = [r for r in ethdb if r[0] == mac]
            if len(record) == 0:
                print red("Unable to get hostname of ip=%s(MAC=%s). Not stored in iptraf database." % (ip, mac))
                continue
            else:
                print green("%s -> %s -> %s" % (ip, mac, record[0][1]))
        
    
@roles('firewall')
@task
def mac(*args):
    """ Find machine name by mac-address """
    if len(args) < 1:
        usage()
    ethdb, arpdb = get_db()
    for mac in args:
        mac_ = mac.replace(":", "").upper()
        record = [r for r in ethdb if r[0] == mac_]
        if len(record) == 0:
            print red("Unable to get hostname of MAC=%s. Not stored in iptraf database." % mac)
            continue
        else:
            print green("%s -> %s" % (mac, record[0][1]))
            
        
    

