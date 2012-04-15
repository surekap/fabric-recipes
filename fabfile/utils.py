"""
Utility functions for uploading config files
"""
from fabric.api import run, put, env, hide
from fabric.contrib.files import exists
import datetime, uuid, os

def reconfigure(src, params, dest, mode=644, backup=True):
    """ Upload the config file. """
    with open(os.path.join("templates", src), "rb") as in_fp:
        data = in_fp.read()
        data = data % params
        
        # Check if remote file is same as config (in which case, dont bother)
        if exists(dest):
            remote_data = run("cat %s" % dest)
            if data.strip() == remote_data.strip():
                return False
        
        if backup:
            backup_if_exists(dest)
        
        tmpfn = uuid.uuid1().hex
        ini_file = os.path.join("templates", tmpfn)
        try:
            with open(ini_file, "wb") as out_fp:
                out_fp.write(data)
            
            out = put(ini_file, dest, mode=mode)
            return True
        finally:
            os.remove(ini_file)
    return False

def backup_if_exists(path):
    """ Backup a remote file, if it exists. """
    if exists(path):
        tstamp = datetime.datetime.now().toordinal()
        run("mv %s %s.%s" % (path, path, tstamp))
        return True
    else:
        return False
    

def is_debian_or_ubuntu():
    with hide("running", "stdout", "stderr"):
        s = run("cat /etc/issue")
        s = s.lower()
        return s.find("ubuntu") > -1 or s.find("debian") > -1

def is_not_server():
    ip = env.host
    quartets = ip.split(".")
    last = int(quartets[-1])
    # If the current host ip > 192.168.0.100
    if last > 100:
        return True
    return False