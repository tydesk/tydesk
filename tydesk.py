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
import tknotify

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

def GetAppsCache():
  return expanduser("~") + r"\tyout.json"

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
    self.root.style.configure("TY.TButton", font=(u'微软雅黑', 12))
    self.root.style.configure("RW.TButton", font=(u'微软雅黑', 12), foreground="red", background="white", width=25)
    self.root.style.configure("BW.TButton", font=(u'微软雅黑', 12), foreground="black", background="white", width=25)

    self.root.resizable(0,0)
    self.LoadConfig()
    self.GetAlerts()
    self.connectServer()
    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    self.root.mainloop()

  def on_closing(self):
    if tkMessageBox.askokcancel(u"退出统医桌面", u"确定退出统医桌面吗？"):
      self.root.destroy()
  
  def GetAlerts(self):
    try:  
      url = "http://" + self.host  + r"/ty/alerts?uid=" + GetUID()
      r = requests.get(url, timeout=0.1)
      if r.json()['count'] > 0:
        tknotify.show(title=u"告警！请处理")
    except requests.exceptions.RequestException as e:
      pass
    if self.RTM.lower() in ("yes", "true", "t", "1"):    
      delay = 5*1000
    else:
      delay = 30*60*1000
    self.root.after(delay, self.GetAlerts)

  def connectServer(self):
    try:
      osName = platform.system() + " " + platform.release()
      payload = {"net": self.net, "uid": GetUID(), "os": osName, "ip": GetIP(), "usb": GetUSBStor()}            
      url = "http://" + self.host  + r"/connect"      
      r = requests.post(url, data=payload, timeout=0.1)      
      self.msg = r.json()['msg']
      self.apps = r.json()['apps']
      with open(GetAppsCache(), 'w+') as outfile:
        json.dump(r.json(), outfile)
    except requests.exceptions.RequestException as e:
      self.msg = "离线运行"
      if os.path.isfile(GetAppsCache()):
        with open(GetAppsCache(), 'r') as json_data:
          d = json.load(json_data)
          self.apps = d
      else:
        self.apps = []

    self.BuildUI()
    self.root.after(30*60*1000, self.connectServer)

  def BuildUI(self):
    fnt = tkFont.Font(family="Arial Bold", size=18)
    fnt2 = tkFont.Font(family="Arial Bold", size=28)
    if self.frame is not None:
      self.frame.destroy()
    self.frame = Frame(self.root)
    self.frame.pack()
    self.root.title(u"统医桌面 tydesk.com")

    self.labelWeb = Label(self.frame, text=u"网页应用", font=fnt)    
    self.labelWeb.grid(row=0, column=0, pady=15)
    btn = Button(self.frame, text=u"查看消息", style="BW.TButton", command=partial(self.ShowMessages))
    btn.grid(row=1, column=0, sticky='WENS', padx=5, ipady=5)
   
    idx = 2
    for app in self.apps:
      if app.get('col') == 1 and self.net == app['net']:
        btn = Button(self.frame, text=app['title'], style="TY.TButton", width=15, 
          command= partial(self.OnClickWeb, open=app['open'], url=app['url'], id=app['id']))
        btn.grid(row=idx, column=0, sticky='WENS', padx=5, ipady=5)
        idx = idx + 1

    self.labelDesk = Label(self.frame, text=u"桌面应用", font=fnt)    
    self.labelDesk.grid(row=0, column=1, pady=15)

    if self.msg == 'ok':
      btn = Button(self.frame, text=u"本机信息", style="BW.TButton", command=partial(self.OpenWeb))      
    else:
      btn = Button(self.frame, text=self.msg, style="RW.TButton", command=partial(self.OpenWeb))
    btn.grid(row=1, column=1, sticky='WENS', padx=5, ipady=5)

    idx = 2
    for app in self.apps:
      if app.get('col') == 2 and self.net == app['net'] and os.path.isfile(app['url']):
        btn = Button(self.frame, text=app['title'], style="TY.TButton", width=15, 
          command= partial(self.OnClickDesktop, open=app['open'], url=app['url'], id=app['id']))
        btn.grid(row=idx, column=1, sticky='WENS', padx=5, ipady=5)
        idx = idx + 1

    self.label = Label(self.frame, text=u"门诊相关", font=fnt)
    self.entry = Entry(self.frame, width=10, font=fnt2)
    self.label.grid(row=0, column=2, padx=(50, 5), pady=15)
    self.entry.grid(row=1, column=2, padx=(50, 5))
    idx = 2
    for app in self.apps:
      if app.get('col') == 3 and self.net == app['net']:
        btn = Button(self.frame, text=app['title'], style="TY.TButton", width=15, 
          command= partial(self.OnClickOutBtn, open=app['open'], url=app['url'], id=app['id']))
        btn.grid(row=idx, column=2, sticky='WENS', padx=(50, 5), ipady=5)
        idx = idx + 1


    self.label2 = Label(self.frame, text=u"住院相关", font=fnt)
    self.entry2 = Entry(self.frame, width=10, font=fnt2)
    self.label2.grid(row=0, column=3, pady=15)
    self.entry2.grid(row=1, column=3, padx=5)
    idx = 2
    for app in self.apps:
      if app.get('col') == 4 and self.net == app['net']:
        btn = Button(self.frame, text=app['title'], style="TY.TButton", width=15,
          command= partial(self.OnClickInBtn, open=app['open'], url=app['url'], id=app['id']))
        btn.grid(row=idx, column=3, sticky='WENS', padx=5, ipady=5)
        idx = idx + 1

  
  def ShowMessages(self):
    url = "http://" + self.host  + r"/ty/messages?uid=" + GetUID()
    chrome_path = find_chrome_win()        
    if (chrome_path is not None): 
      subprocess.call([chrome_path, url])
    else:
      ie = webbrowser.get(webbrowser.iexplore)    
      ie.open(url)
  def OpenWeb(self):
    url = "http://" + self.host  + r"/ty/index?uid=" + GetUID()
    chrome_path = find_chrome_win()        
    if (chrome_path is not None): 
      subprocess.call([chrome_path, url])
    else:
      ie = webbrowser.get(webbrowser.iexplore)    
      ie.open(url)

  def OnClickOutBtn(self, open, url, id):
    num = self.entry.get().strip()
    self.OnClick(open, url, num, id)

  def OnClickInBtn(self, open, url, id):
    num = self.entry2.get().strip()
    self.OnClick(open, url, num, id)

  def OnClickWeb(self, open, url, id):
    self.OnClick(open, url, "", id)

  def OnClickDesktop(self, open, url, id):
    p = subprocess.Popen('start /B "" "' + url + '"', shell=True)
    p.wait()

  def OnClick(self, open, url, num, id):    
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
      self.RTM = self.config["real.time"]
      self.ip = GetIP()

      if self.ip[:self.ip.find('.')] == self.innerHost[:self.innerHost.find('.')]:        
        self.host = self.innerHost + ":5678"
        self.net = 'in'
      else:
        self.host = self.outerHost + ":5678"
        self.net = 'out'
    else:
      sys.exit()

app = App()