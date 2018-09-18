#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import configobj
import sys, os, time
import socket
from datetime import datetime
import subprocess

if os.path.isfile('tydclient.exe'):
  mtime = datetime.fromtimestamp(os.path.getmtime('./tydclient.exe')).strftime('%Y-%m-%d %H:%M:%S')
else:
  mtime = ''


try:
  host = "https://tydesk.com"
  r = requests.get(host + "/get/mtime", timeout=0.1)
  if r.json()['mtime'] == mtime:
    pass
  else:
    req = requests.get(host + "/download", stream=True)
    with open('tydclient.exe', 'wb') as f:
      for chunk in req.iter_content(chunk_size=1024): 
        if chunk:
          f.write(chunk)
except requests.exceptions.RequestException as e:
  pass

subprocess.Popen('start /B "" "tydclient.exe"', shell=True)