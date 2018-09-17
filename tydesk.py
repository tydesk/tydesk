#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import configobj
import sys, os, time
import socket
from datetime import datetime
import subprocess


def GetIP():
  return socket.gethostbyname(socket.gethostname())

def download_file(url):
  local_filename = url.split('/')[-1]
  # NOTE the stream=True parameter
  r = requests.get(url, stream=True)
  with open(local_filename, 'wb') as f:
    for chunk in r.iter_content(chunk_size=1024): 
      if chunk: # filter out keep-alive new chunks
        f.write(chunk)
        #f.flush() commented by recommendation from J.F.Sebastian
  return local_filename
    
iniFile = "config.ini"  
if os.path.isfile(iniFile):
  config = configobj.ConfigObj(iniFile)
  inner = config["internal.host"]
  nums = inner.split('.')
  port= config["port"]
  if GetIP().startswith(nums[0]):
    host= config["internal.host"]
  else:
    host= config["external.host"]
else:
  sys.exit(0)


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