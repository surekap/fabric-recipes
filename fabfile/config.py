"""
Set the configuration variables for fabric recipes.
"""

from fabric.api import env

env.roledefs.update({
    'firewall':['root@192.168.0.1'],
    'web':['root@192.168.0.4']
})



# ntp_client:
TIME_SERVER = "192.168.0.4"
TIMEZONE = "Asia/Calcutta"

# cups_client:
CUPS_SERVER = "192.168.0.6"

# snmp: snmpd client settings
SNMP_PUBLIC = "public"
SNMP_LOCATION = "123 Main Street"
SNMP_CONTACT = "nobody@nobody.com"
SNMP_NET = "192.168.0.0/24"

# syslog_client: Syslog client settings
LOG_SERVER = "192.168.0.6"
LOG_PROTO = "udp"
LOG_PORT = "514"
LOG_SCOPE = "*.*"

# web: web server settings
WEB_DOMAIN = "mydomain.com"
WEB_SSL_CERTIFICATE = "/etc/nginx/ssl/mydomain.com.crt"
WEB_SSL_CERTIFICATE_KEY = "/etc/nginx/ssl/mydomain.com.key"
