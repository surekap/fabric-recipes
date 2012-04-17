from fabric.api import env, run
from utils import reconfigure
env.warn_only = True

def config():
    """ Set the locale to be:
        en_IN UTF-8
        en_US ISO-8859-1
        en_US.UTF-8 UTF-8
    """
    reconfigure("locale.template", {}, "/etc/locale.gen")
    run("/usr/sbin/locale-gen")

