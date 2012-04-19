"""
Set the configuration variables for fabric recipes.
"""

from fabric.api import env
from fabric.colors import yellow
import os
env.warn_only = True

try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp   # Python 3.0


config = {}

_config = cp.SafeConfigParser()
if not os.path.isfile("fabric-recipes.conf"):
    print yellow("warning: No config file specified")
    
_config.read("fabric-recipes.conf")

for section in _config.sections():
    opt = _config.items(section)
    if section == "global":
        env.update(opt)
    elif section == "roledefs":
        opt = [(k, v.split(",")) for k, v in opt]
        env['roledefs'].update(opt)
    else:
        config[section] = dict(opt)