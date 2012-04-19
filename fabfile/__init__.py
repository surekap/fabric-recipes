"""
Initialization code for fabric-recipes here.
"""
__version__ = "0.1.0"
__author__ = "Prateek Sureka"

from config import config
import apt
import cups_client
import hosts
import locale_gen
import lsof
import ntp_client
import pkgsync
import service
import snmp
import syslog_client
import webmin
import web
import whois


# TODO:
# hosts.ensure_fromfile
# hosts.file_to_iptraf

# fab -P -z 5 --skip-bad-hosts -R clients apt.deploy
# fab -P -z 5 --skip-bad-hosts -R clients apt.ensure:apt-show-versions=installed
# fab -P -z 5 --skip-bad-hosts -R clients syslog_client.deploy locale_gen.config ntp_client.deploy cups_client.deploy snmp.deploy
# fab -P -z 5 --skip-bad-hosts -R clients snmp.deploy
