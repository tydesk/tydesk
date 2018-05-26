#!/usr/bin/env python
#coding:utf-8
from Tkinter import *
from ttk import *
import tkFont
import os, sys, re
import configobj
import os.path
from os.path import expanduser
import requests
import platform
import json
import socket
from functools import partial
import subprocess
import webbrowser
import tkMessageBox
import time
import winreg as reg

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

def find_chrome_win():
  reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'

  for install_type in reg.HKEY_LOCAL_MACHINE, reg.HKEY_CURRENT_USER:
      try:
          reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
          chrome_path = reg.QueryValue(reg_key, None)
          reg_key.Close()
      except WindowsError:
          pass

  return chrome_path

def find_firefox_win():
  reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe'

  for install_type in reg.HKEY_LOCAL_MACHINE, reg.HKEY_CURRENT_USER:
      try:
          reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
          firefox_path = reg.QueryValue(reg_key, None)
          reg_key.Close()
      except WindowsError:
          pass

  return firefox_path

def GetUSBStor():
  aReg = reg.ConnectRegistry(None, reg.HKEY_LOCAL_MACHINE)
  try:
    aKey = reg.OpenKey(aReg, r"SYSTEM\CurrentControlSet\Services\USBSTOR", 0, reg.KEY_ALL_ACCESS)            
  except WindowsError:
    aKey = reg.CreateKey(aReg, r"SYSTEM\CurrentControlSet\Services\USBSTOR")

  value, regtype = reg.QueryValueEx(aKey, "Start")
  reg.CloseKey(aKey)
  reg.CloseKey(aReg)
  return value

def GetIP():
  return socket.gethostbyname(socket.gethostname())

def GetOutCache():
  return expanduser("~") + r"\tyout.json"

def GetInCache():
  return expanduser("~") + r"\tyin.json"

def GetOtherCache():
  return expanduser("~") + r"\tyother.json"

def GetUID():
  path = expanduser("~") + r"\pcuid.txt"
  with open(path, 'w') as f:
    try:            
      txt = subprocess.check_output(["wmic","csproduct","get", "uuid"], **subprocess_args(False)).strip().split("\n")[1]                    
      f.write(txt)
      uid = txt
    except OSError as e:
      f.write('Failed: ' + str(e))
      uid = ''
  return uid

class App():
  def __init__(self):
    self.frame = None
    self.root = Tk()
    self.root.style = Style()
    self.root.style.theme_use("clam")
    self.root.resizable(0,0)
    self.LoadConfig()    
    self.LoadData()
    self.connectServer()    
    self.root.mainloop()

  def connectServer(self):
    try:
      osName = platform.system() + " " + platform.release()
      payload = {"net": self.net, "uid": GetUID(), "os": osName, "ip": GetIP(), "usb": GetUSBStor()}            
      url = "http://" + self.host  + r"/connect"      
      r = requests.post(url, data=payload, timeout=0.1)
    except requests.exceptions.RequestException as e:
      pass
    self.BuildUI()
    self.root.after(30*60*1000, self.connectServer)

  def BuildUI(self):
    fnt = tkFont.Font(size=24)
    fnt2 = tkFont.Font(family="Arial Bold", size=36)
    if self.frame is not None:
      self.frame.destroy()
    self.frame = Frame(self.root)
    self.frame.pack()
    self.root.title(u"统医桌面 tydesk.com")

    self.label = Label(self.frame, text=u"门诊相关", font=fnt)
    self.entry = Entry(self.frame, width=12, font=fnt2)
    self.label.grid(row=0, column=0, pady=10)
    self.entry.grid(row=1, column=0, padx=10)
    idx = 2
    for app in self.OutItems:
      if app.get('net') and self.net == app['net']:
        btn = Button(self.frame, text=app['title'], width=15, 
          command= partial(self.OnClickOutBtn, open=app['open'], url=app['url']))
        btn.grid(row=idx, column=0, sticky='WENS', padx=10, ipady=5)
        idx = idx + 1

    lblx = Label(self.frame, text=u"")
    lblx.grid(row=idx, column=0)


    self.label2 = Label(self.frame, text=u"住院相关", font=fnt)
    self.entry2 = Entry(self.frame, width=12, font=fnt2)
    self.label2.grid(row=0, column=1, pady=10)
    self.entry2.grid(row=1, column=1, padx=10)
    idx = 2
    for app in self.InItems:
      if app.get('net') and self.net == app['net']:
        btn = Button(self.frame, text=app['title'], width=15,
          command= partial(self.OnClickInBtn, open=app['open'], url=app['url']))
        btn.grid(row=idx, column=1, sticky='WENS', padx=10, ipady=5)
        idx = idx + 1
    lblx1 = Label(self.frame, text=u"")
    lblx1.grid(row=idx, column=1)

    self.label3 = Label(self.frame, text=u"其他系统", font=fnt)
    self.label3.grid(row=0, column=2, padx=(100,100), pady=10)
    btn = Button(self.frame, text=u"统医桌面WEB版", width=50, command=partial(self.OpenWeb))
    btn.grid(row=1, column=2, sticky='WENS', padx=10, ipady=5)

    idx = 2
    for app in self.OtherItems:
      if app.get('net') and self.net == app['net']:
        btn = Button(self.frame, text=app['title'], width=50,
          command= partial(self.OnClick, open=app['open'], url=app['url']))
        btn.grid(row=idx, column=2, sticky='WENS', padx=10, ipady=5)
        idx = idx + 1
    lblx2 = Label(self.frame, text=u"")
    lblx2.grid(row=idx, column=2)
  
  def OpenWeb(self):
    url = "http://" + self.host  + r"/ty/index?uid=" + GetUID()
    chrome_path = find_chrome_win()        
    if (chrome_path is not None): 
      subprocess.call([chrome_path, url])
    else:
      ie = webbrowser.get(webbrowser.iexplore)    
      ie.open(url)

  def OnClickOutBtn(self, open, url):
    num = self.entry.get().strip()
    self.OnClick(open, url, num)

  def OnClickInBtn(self, open, url):
    num = self.entry2.get().strip()
    self.OnClick(open, url, num)

  def OnClick(self, open, url, num):
    if "__" in url:
      if len(num) > 0:
        url = url.replace("__", num)
      else:
        tkMessageBox.showinfo(u"提示", u"请提供病人号")
        return
      
    if (open == 'IE'):
      ie = webbrowser.get(webbrowser.iexplore)
      ie.open(url)
      return

    if (open == 'chrome'):
      if sys.platform in ['win32', 'win64']:
        chrome_path = find_chrome_win()        
        if (chrome_path is not None): 
          subprocess.call([chrome_path, url])
        else:
          tkMessageBox.showinfo(u"提示", u"谷歌浏览器未安装")
          return
      else:
        webbrowser.get('chrome').open_new_tab(url)

    if (open == 'firefox'):
      if sys.platform in ['win32', 'win64']:
        firefox_path = find_firefox_win()        
        if (firefox_path is not None): 
          subprocess.call([firefox_path, url])
        else:
          tkMessageBox.showinfo(u"提示", u"火狐浏览器未安装")
          return
      else:
        webbrowser.get('firefox').open_new_tab(url)

  def LoadConfig(self):
    iniFile = "config.ini"
    if os.path.isfile(iniFile):
      self.config = configobj.ConfigObj(iniFile)
      self.innerHost = self.config["inner.host"]
      self.outerHost = self.config["outer.host"]
      self.ip = GetIP()

      if self.ip[:self.ip.find('.')] == self.innerHost[:self.innerHost.find('.')]:        
        self.host = self.innerHost + ":5678"
        self.net = 'in'
      else:
        self.host = self.outerHost + ":5678"
        self.net = 'out'
    else:
      sys.exit()

  def LoadData(self):
    try:
      r = requests.get("http://" + self.host + "/outApps", timeout=0.1)
      self.OutItems = r.json()     
      with open(GetOutCache(), 'w+') as outfile:
        json.dump(r.json(), outfile)
    except requests.exceptions.RequestException as e:
      if os.path.isfile(GetOutCache()):
        with open(GetOutCache(), 'r') as json_data:
          d = json.load(json_data)
          self.OutItems = d
      else:
        self.OutItems = []

    try:
      r = requests.get("http://" + self.host + "/inApps", timeout=0.1)
      self.InItems = r.json()     
      with open(GetInCache(), 'w+') as outfile:
        json.dump(r.json(), outfile)
    except requests.exceptions.RequestException as e:
      if os.path.isfile(GetInCache()):
        with open(GetInCache(), 'r') as json_data:
          d = json.load(json_data)
          self.InItems = d
      else:
        self.InItems = []

    try:
      r = requests.get("http://" + self.host + "/otherApps", timeout=0.1)
      self.OtherItems = r.json()     
      with open(GetOtherCache(), 'w+') as outfile:
        json.dump(r.json(), outfile)
    except requests.exceptions.RequestException as e:
      if os.path.isfile(GetOtherCache()):
        with open(GetOtherCache(), 'r') as json_data:
          d = json.load(json_data)
          self.OtherItems = d
      else:
        self.OtherItems = []

app = App()