#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os
from os.path import expanduser
import socket
import configobj

def server():
  return "https://tydesk.com"

def ip():
  return socket.gethostbyname(socket.gethostname())

def config():
  iniFile = "config.ini"
  config = configobj.ConfigObj(iniFile)
  key = config["key"]
  return key

def subprocess_args(include_stdout=True):
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    #
    #   Traceback (most recent call last):
    #     File "test_subprocess.py", line 58, in <module>
    #       **subprocess_args(stdout=None))
    #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
    #       raise ValueError('stdout argument not allowed, it will be overridden.')
    #   ValueError: stdout argument not allowed, it will be overridden.
    #
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret

def pcid():
  pcid = ''
  out = expanduser("~") + r"\pcbox.txt"
  with open(out, 'w') as f:
    try:            
      txt = subprocess.check_output(["wmic","csproduct","get", "uuid"], **subprocess_args(False)).strip().split("\n")[1]                    
      f.write(txt)
      pcid = txt
    except OSError as e:
      f.write('Failed: ' + str(e))
      pcid = ''
  return pcid