#!/bin/env python
"""
#######################################################################
#                                                                     #
# Copyright (c) 2012, Prateek Sureka. All Rights Reserved.            #
# This module provides an idempotent mechanism to remotely configure  #
# web proxies a host.                                                 #
#                                                                     #
#######################################################################
"""

from fabric.api import task, run, env, roles
from fabric.contrib.files import exists
from fabric.colors import red, green
from utils import reconfigure
from config import WEB_DOMAIN, WEB_SSL_CERTIFICATE, WEB_SSL_CERTIFICATE_KEY
import sys

env.warn_only = True

def usage():
    """ Print help string """
    print "fab -H <host> web.enabled:ldapadmin=http://127.0.0.1:81/phpldapadmin,monitor=http://192.168.0.99:8080"
    print "fab -H <host> web.disabled:ldapadmin=http://127.0.0.1:81/phpldapadmin,monitor=http://192.168.0.99:8080"
    print "fab -H <host> web.status:ldapadmin,monitor"
    sys.exit(1)

@roles('web')
@task
def enabled(**kwargs):
    """ Ensure nginx web proxying to a sub-domain is enabled """
    if len(kwargs) < 1:
        usage()
    changed = False
    web_domain, web_ssl_certificate, web_ssl_certificate_key = (WEB_DOMAIN, WEB_SSL_CERTIFICATE, WEB_SSL_CERTIFICATE_KEY)
    for sub, url in kwargs.iteritems():
        template = "web_nginx.template"
        if url.lower().startswith("https:"):
            template = "web_ssl_nginx.template"
        changed = changed or reconfigure(template, locals(), "/etc/nginx/sites-available/%s" % sub)
        if not exists("/etc/nginx/sites-enabled/%s" % sub):
            changed = True
            run("ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s" % (sub, sub))
    if changed:
        import service
        service.ensure(nginx="restarted")

@roles('web')
@task 
def disabled(**kwargs):
    """ Ensure nginx web proxying to a sub-domain is disabled """
    if len(kwargs) < 1:
        usage()
    changed = False
    web_domain, web_ssl_certificate, web_ssl_certificate_key = (WEB_DOMAIN, WEB_SSL_CERTIFICATE, WEB_SSL_CERTIFICATE_KEY)
    for sub, url in kwargs.iteritems():
        template = "web_nginx.template"
        if url.lower().startswith("https:"):
            template = "web_ssl_nginx.template"
        # reconfiguration doesn't matter in this case
        reconfigure(template, locals(), "/etc/nginx/sites-available/%s" % sub)
        if exists("/etc/nginx/sites-enabled/%s" % sub):
            changed = True
            run("rm /etc/nginx/sites-enabled/%s" % sub)
    if changed:
        import service
        service.ensure(nginx="restarted")

@roles('web')
@task
def status(*args):
    """ Get status of nginx web proxying to a sub-domain. """
    if len(args) < 1:
        usage()
    for sub in args:
        print "%s: " % sub,
        if exists("/etc/nginx/sites-enabled/%s" % sub):
            print green("enabled")
        else:
            print red("disabled")
        
    

