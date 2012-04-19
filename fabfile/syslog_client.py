#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent mechanism to remotely configure  #
# syslog/rsyslog on a host to send messages to a server.              #
#                                                                     #
#######################################################################
"""

from fabric.api import task, env, cd, run, hide
from fabric.contrib.files import exists, upload_template
from fabric.colors import red, green
from utils import is_debian_or_ubuntu

from config import config
import os, uuid

env.warn_only = True

def usage():
    """ Print the help string. """
    print "fab -H <host> syslog_client.deploy:server=192.168.0.6,proto=udp,port=514,scope=*.*"

@task
def deploy(server=config.get("syslog_client", {}).get("syslog_server", ""),
            proto=config.get("syslog_client", {}).get("syslog_proto", ""),
            port=config.get("syslog_client", {}).get("syslog_port", ""),
            scope=config.get("syslog_client", {}).get("syslog_scope", "")):
    """ Configure and re-start syslog. """
    if not is_debian_or_ubuntu():
        print red("Cannot deploy to non-debian/ubuntu host: %s" % env.host)
        return
    
    with cd("/etc/init.d"):
        svcn = run("ls -1 *sys*log*")
        svcn = svcn.split("\n")[0]
        
    if exists("/etc/syslog.conf"):
        conf = "/etc/syslog.conf"
    elif exists("/etc/rsyslog.conf"):
        conf = "/etc/rsyslog.conf"
    
    with hide("running", "stdout", "stderr"):
        config = run("cat %s" % conf)
    line = "%s  %s%s:%s" % (scope, "@@" if proto == "tcp" else "@", server, port)
    
    if config.find(server) > -1:
        # Check if current config matches existing config
        if config.find(line) > -1:
            print green("%s: No changes necessary" % env.host)
            return True
        else:
            config_lines = config.split("\n")
            for i, l in enumerate(config_lines):
                if l.find(server) > -1:
                    config_lines[i] = line
                    break
            config = "\n".join(config_lines)
            config += "\n"
    else:
        config = ("\n" + line + "\n") + config
        config = config.replace("\n\n", "\n")
    
    fn = os.path.join("templates", uuid.uuid1().hex)
    
    with open(fn, "wb") as outf:
        outf.write(config)
    
    # Put the file on the server
    upload_template(fn, conf)
    os.remove(fn)
    
    kw = {}
    kw[svcn] = "restarted"
    import service
    service.ensure(**kw)
