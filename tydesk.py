#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os, os.path
import wx.lib.agw.toasterbox as TB
import requests
import subprocess
from os.path import expanduser
import platform
import json
import wx.lib.scrolledpanel as scrolled
import wx.lib.buttons as buttons
import time
import math
import hashlib, binascii
import tydhost as TH
import browsers

def GetMainToken(salt, input_pwd):
  fromHex_salt = binascii.a2b_hex(salt)    
  dk = hashlib.pbkdf2_hmac('sha1', input_pwd.encode('utf-8'), fromHex_salt, 1000, dklen=32)
  return binascii.hexlify(dk).decode('utf-8')
  
def OpenWith(flag, url):
  CheckinJsonFile = expanduser("~") + r"\tyd_checkin.json"

  if os.path.isfile(CheckinJsonFile):
    emp = ""       
    with open(CheckinJsonFile, 'r') as json_data:
      CheckinData = json.load(json_data)
      emp = CheckinData['emp']
  else:
    wx.MessageBox(u'请先签到', u'提示')
    return

  if not emp:
    wx.MessageBox(u'请先签到', u'提示')
    return
    

  if (flag == 'Exe'):
    subprocess.Popen('start /B "" "' + url + '"', shell=True)
  else:
    if '?' in url:
      url = url + '&tyd_emp=' + emp + '&tyd_pc=' + TH.pcid()
    else:
      url = url + '?tyd_emp=' + emp + '&tyd_pc=' + TH.pcid()

    if (flag == 'Chrome'):
      chrome_path = browsers.find_chrome_win()        
      if (chrome_path is not None):
        subprocess.Popen(chrome_path + ' "'+url+'"')
      else:
        wx.MessageBox(u'请安装谷歌浏览器', u'提示')
        return

    if (flag == 'Firefox'):
      firefox_path = browsers.find_firefox_win()        
      if (firefox_path is not None):
        subprocess.Popen(firefox_path + ' "'+url+'"')
      else:
        wx.MessageBox(u'请安装火狐浏览器', u'提示')
        return
        
    if (flag == 'IE'):
      ie = webbrowser.get(webbrowser.iexplore)
      ie.open(url)

  return

def GetToken():
  tokenJson = expanduser("~") + r"\tyd_token.json"
  if os.path.isfile(tokenJson):          
    with open(tokenJson, 'r') as json_data:
      tokenData = json.load(json_data)
      try:
        return tokenData['token']
      except KeyError as err:
        return None
  else:
    return None

class Link(wx.StaticText):
  def __init__(self, *args, **kw):
    super(Link, self).__init__(*args, **kw)

    self.font1 = wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL, True, u'微软雅黑')
    self.font2 = wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'微软雅黑')

    self.SetFont(self.font2)
    self.SetForegroundColour('#0000ff')

    self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
    self.Bind(wx.EVT_MOTION, self.OnMouseEvent)

  def SetUrl(self, url):
    self.url = url

  def SetOpenWith(self, openWith):
    self.openWith = openWith


  def OnMouseEvent(self, e):
    if e.Moving():
      self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
      self.SetFont(self.font1)

    elif e.LeftUp():
      OpenWith(self.openWith, self.url)
    else:
      self.SetCursor(wx.NullCursor)
      self.SetFont(self.font2)
    e.Skip()

class RegisterDialog(wx.Dialog):
  def __init__(self, *args, **kw):
    super(RegisterDialog, self).__init__(*args, **kw)

    self.InitUI()
    self.SetSize((250, 250))
    self.SetTitle(u"终端接入")

  def InitUI(self):
    pnl = wx.Panel(self)
    vbox = wx.BoxSizer(wx.VERTICAL)

    sb = wx.StaticBox(pnl, label=u'终端接入验证')
    sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

    sbs.Add(wx.StaticText(pnl, -1, u'接入代码'), 0, wx.ALL|wx.EXPAND, 5)
    self.tcRegister = wx.TextCtrl(pnl)
    sbs.Add(self.tcRegister, 0, wx.ALL|wx.EXPAND, 5)

    sbs.Add(wx.StaticText(pnl, -1, u'接入理由（位置、使用者、分机）'), 0, wx.ALL|wx.EXPAND, 5)
    self.tcMemo = wx.TextCtrl(pnl)
    sbs.Add(self.tcMemo, 0, wx.ALL|wx.EXPAND, 5)
    
    pnl.SetSizer(sbs)

    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    okButton = wx.Button(self, label=u'确认')
    closeButton = wx.Button(self, label=u'取消')
    hbox2.Add(okButton)
    hbox2.Add(closeButton, flag=wx.LEFT, border=5)

    vbox.Add(pnl, 0, wx.ALL|wx.EXPAND, 5)
    vbox.Add(hbox2, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, 10)

    self.SetSizer(vbox)
    self.Layout()

    okButton.Bind(wx.EVT_BUTTON, self.OnEnterCode)
    closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
  
  def OnClose(self, e):
    self.Destroy()

  def OnEnterCode(self, e):
    tokenJson = expanduser("~") + r"\tyd_token.json"
    key = TH.config()
    code = self.tcRegister.GetValue()
    osname = platform.system() + "_" + platform.release()
    try:
      data = {
        "code": self.tcRegister.GetValue(),
        "memo": self.tcMemo.GetValue()
      }

      r = requests.post(TH.server() + "/api/register/" + key + "/" + TH.pcid() + "/" + TH.ip() + "/" + TH.model() + "/" + osname, data=data, timeout=3)
      with open(tokenJson, 'w+') as outfile:
        json.dump(r.json(), outfile)
        
      ok = r.json()['ok']
      if ok == 0:
        wx.MessageBox(u'信息有误，请联系贵方管理员', u'提示')
      if ok == 1:
        token = r.json()['token']
        wx.MessageBox(u'接入成功，请重启客户端', u'提示')
      pass
    except requests.exceptions.RequestException as e:
      print e
      wx.MessageBox(u'网络故障，请一会儿重试', u'提示')
      return False
    
    self.Destroy()


class CheckinDialog(wx.Dialog):
  def __init__(self, *args, **kw):
    super(CheckinDialog, self).__init__(*args, **kw)

    self.InitUI()
    self.SetSize((250, 150))
    self.SetTitle(u"员工签到")

  def InitUI(self):
    pnl = wx.Panel(self)
    vbox = wx.BoxSizer(wx.VERTICAL)

    sb = wx.StaticBox(pnl, label=u'请输入员工号')
    sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
    self.tcCheckin = wx.TextCtrl(pnl)
    sbs.Add(self.tcCheckin, 0, wx.ALL|wx.EXPAND, 5)
    
    pnl.SetSizer(sbs)

    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    okButton = wx.Button(self, label=u'确认')
    closeButton = wx.Button(self, label=u'取消')
    hbox2.Add(okButton)
    hbox2.Add(closeButton, flag=wx.LEFT, border=5)

    vbox.Add(pnl, 0, wx.ALL|wx.EXPAND, 5)
    vbox.Add(hbox2, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, 10)

    self.SetSizer(vbox)
    self.Layout()

    okButton.Bind(wx.EVT_BUTTON, self.OnConfirm)
    closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
  
  def OnClose(self, e):
    self.Destroy()

  def OnConfirm(self, e):
    tokenJson = expanduser("~") + r"\tyd_token.json"
    key = TH.config()
    emp = self.tcCheckin.GetValue()
    if not emp:
      wx.MessageBox(u'员工号不能为空', u'错误')
      return

    try:
      r = requests.get(TH.server() + "/checkin/" + key + "/" + TH.pcid() + "/" + GetToken() + "/" + emp, timeout=3)              
      ok = r.json()['ok']
      if ok == 0:
        wx.MessageBox(u'信息有误，请联系贵方管理员', u'提示')
      else:
        if ok == 1:
          wx.MessageBox(u'签到成功！', u'提示')
          self.GetParent().stClock.SetLabel(u'工号：'+emp)
        if ok == 2:
          wx.MessageBox(u'今天已经签到过', u'提示')
          self.GetParent().stClock.SetLabel(u'工号：'+emp)
        
        CheckinData = {
          "emp": emp,
          "at": time.time()
        }
        CheckinJsonFile = expanduser("~") + r"\tyd_checkin.json"
        with open(CheckinJsonFile, 'w+') as outfile:
          json.dump(CheckinData, outfile) 

        self.GetParent().stClock.Wrap(80)
        self.GetParent().Layout()
      pass
    except requests.exceptions.RequestException as e:
      wx.MessageBox(u'网络故障，请一会儿重试', u'提示')
      return False
    
    self.Destroy()

class TydMainFrame(wx.Frame):
  def __init__(self, parent, id, title):
    no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
    wx.Frame.__init__(self, parent, id, title, size=(600, 600), style=no_resize)

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.vbox = wx.BoxSizer(wx.VERTICAL)
    
    self.pLeft = scrolled.ScrolledPanel(self, -1, size=(360, 600))
    pRight = scrolled.ScrolledPanel(self, -1, size=(240, 600))
    self.SetBackgroundColour('#F2F2F2')
    self.pLeft.SetBackgroundColour('#F2F2F2')
    pRight.SetBackgroundColour('#D8D8D8')

    gs = wx.BoxSizer(wx.VERTICAL)
    
    gs.AddSpacer(30)
    self.stStation = wx.StaticText(pRight, -1, '')
    gs.Add(self.stStation, 0, wx.ALIGN_CENTER | wx.ALL, 0) 

    self.btnSta = buttons.GenBitmapTextButton(pRight,-1, label=u" 终端接入", 
        bitmap=wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK), size=(160, 45))
    self.btnSta.Bind(wx.EVT_BUTTON, self.OnRegister)
    gs.Add(self.btnSta, 0, wx.ALIGN_CENTER | wx.ALL, 15) 

    gs.AddSpacer(30)
    gs.Add(wx.StaticLine(pRight), 0, wx.ALL|wx.EXPAND, 5)    
    gs.AddSpacer(30)

    self.stClock = wx.StaticText(pRight, -1, '')
    gs.Add(self.stClock, 0, wx.ALIGN_CENTER | wx.ALL, 0) 

    self.btnCheckin = buttons.GenBitmapTextButton(pRight,-1, label=u" 员工签到", 
        bitmap=wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK), size=(160, 45))
    self.btnCheckin.Bind(wx.EVT_BUTTON, self.OnCheckin)
    gs.Add(self.btnCheckin, 0, wx.ALIGN_CENTER | wx.ALL, 15) 

    gs.AddSpacer(30)
    gs.Add(wx.StaticLine(pRight), 0, wx.ALL|wx.EXPAND, 5)
    gs.AddSpacer(30)

    self.btnMsgs = buttons.GenBitmapTextButton(pRight,-1, label=u"本机消息", 
        bitmap=wx.ArtProvider.GetBitmap(wx.ART_GO_HOME), size=(160, 45))
    self.btnMsgs.Bind(wx.EVT_BUTTON, self.OnMessages)
    gs.Add(self.btnMsgs, 0, wx.ALIGN_CENTER | wx.ALL, 15)


    self.btnPhones = buttons.GenBitmapTextButton(pRight,-1, label=u" 终端列表", 
        bitmap=wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW), size=(160, 45))
    self.btnPhones.Bind(wx.EVT_BUTTON, self.OnPhones)
    gs.Add(self.btnPhones, 0, wx.ALIGN_CENTER | wx.ALL, 15)
    
    pRight.SetSizer(gs)
    pRight.Layout()
    self.pLeft.SetupScrolling()
    pRight.SetupScrolling()
    
    self.RenderUI()
    self.Notify()

    self.timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
    self.timer.Start(5*60*1000)
    
    sizer.Add(self.pLeft, 1, wx.LEFT|wx.EXPAND, 0)    
    sizer.Add(pRight, 1, wx.LEFT|wx.EXPAND, 0)
    self.SetSizer( sizer )
    self.Layout()

  def Notify(self):      
    if hasattr(self, 'TotalMsgs') and self.TotalMsgs > 0:
      toaster = TB.ToasterBox(self, tbstyle=TB.TB_COMPLEX)
      toaster.SetPopupSize((200, 120))
      toaster.SetPopupPauseTime(4000)
      toaster.SetPopupPositionByInt(3)
      toaster.SetPopupBackgroundColour('#F2F5A9')
      
      tbpanel = toaster.GetToasterBoxWindow()
      panel = wx.Panel(tbpanel, -1)
      sizer = wx.BoxSizer(wx.VERTICAL)

      sizer.AddSpacer(10)
      st = wx.StaticText(panel, wx.ID_ANY, label= u'有新消息！')
      sizer.Add(st, 0, wx.ALIGN_CENTER|wx.ALL, 10)

      button = wx.Button(panel, wx.ID_ANY, u"点击查看")
      self.Bind(wx.EVT_BUTTON, self.OnMessages, button)
      sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 10)

      panel.SetSizer(sizer)
      toaster.AddPanel(panel)
      wx.CallLater(1000, toaster.Play)
  
  def onTimer(self, event):
    if self.token is None:
      return False
    try:
      r = requests.get(TH.server() + "/ping/" + TH.config() + "/" + TH.pcid() + "/" + self.token, timeout=10)
      if (r.json()['ok'] == 1):
        self.time = str(r.json()['time'])
        self.TotalMsgs = r.json()['count']
        self.UpdateApps(r.json()['apps'])
      else:
        self.TotalMsgs = 0
    except requests.exceptions.RequestException as e:
      self.TotalMsgs = 0

    CheckinJsonFile = expanduser("~") + r"\tyd_checkin.json"

    if os.path.isfile(CheckinJsonFile):
      with open(CheckinJsonFile, 'r') as json_data:
        data = json.load(json_data)
        if not data['emp']:
          self.stClock.SetLabel(u'请签到')
          self.Layout()

        diff = time.time() - data['at']
        if diff > 8*60*60*1000:
          newdata = {
            "emp": "",
            "at": time.time()
          }
          with open(CheckinJsonFile, 'w+') as outfile:
            json.dump(newdata, outfile)    

    self.Notify()

  def NotReady(self):
    self.vbox.Clear(True)      
    self.vbox.AddSpacer(50)
    stWarn = wx.StaticText(self.pLeft, -1, u'终端尚未接入！请先点击右侧终端接入按钮')
    stWarn.SetForegroundColour((255,0,0))
    self.vbox.Add(stWarn, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 20)
    self.pLeft.SetSizer(self.vbox)
    self.pLeft.Layout()

  def RenderUI(self):
    self.token = GetToken()
    if self.token is None:      
      self.NotReady()
      return False

    key = TH.config()
    dataJson = expanduser("~") + r"\data.json"
    try:
      r = requests.get(TH.server() + "/apps/" + key + "/" + TH.pcid() + "/" + self.token, timeout=3)
      
      if (r.json()['ok'] == 1):        
        self.time = str(r.json()['time'])
        self.stStation.SetLabel(r.json()['location'])
        self.stStation.Wrap(80)
        
        CheckinJsonFile = expanduser("~") + r"\tyd_checkin.json"
        if os.path.isfile(CheckinJsonFile):
          with open(CheckinJsonFile, 'r') as json_data:
            data = json.load(json_data)
            if not data['emp']:
              self.stClock.SetLabel(u'请签到')
            else:
              self.stClock.SetLabel(u'员工：'+data['emp'])
            self.stClock.Wrap(80)
            self.Layout()
        else:
          self.stClock.SetLabel(u'请签到')
          self.Layout()

        self.connected = True
        self.TotalMsgs = r.json()['totalMsgs']
        apps = r.json()['apps']
        with open(dataJson, 'w+') as outfile:
          json.dump(apps, outfile)
        self.UpdateApps(apps)
      else:
        self.connected = False
        self.TotalMsgs = 0  
        self.NotReady()
        return False
    except requests.exceptions.RequestException as e:
      self.connected = False
      self.TotalMsgs = 0
      if os.path.isfile(dataJson):          
        with open(dataJson, 'r') as json_data:
          apps = json.load(json_data)
          self.UpdateApps(apps)

  def UpdateApps(self, data):
    self.vbox.Clear(True)      
    self.vbox.AddSpacer(20)
    for it in data:
      if (it['opw'] == 'Exe'):
        if not os.path.isfile(it['url']):
          continue

      link_wid = Link(self.pLeft, label=it['title'])
      link_wid.SetUrl(it['url'])
      link_wid.SetOpenWith(it['opw'])
      self.vbox.Add(link_wid, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 20)
    self.pLeft.SetSizer(self.vbox)
    self.pLeft.Layout()
   

  def OnHelp(self, event):
    self.token = GetToken()
    if self.token is None:
      wx.MessageBox(u'请先正确接入终端！', u'提示')
      return False

    timestamp = str(int(round(time.time() * 1000)))
    timestamp = self.time if self.time else timestamp
    mt = GetMainToken(self.token, timestamp)
    
    key = TH.config()
    OpenWith('Chrome', TH.server() + "/t/" + key + "/" + mt + "/" + timestamp + "/help")
    return

  def OnPhones(self, event):
    self.token = GetToken()
    if self.token is None:
      wx.MessageBox(u'请先正确接入终端！', u'提示')
      return False
    
    timestamp = str(int(round(time.time() * 1000)))
    timestamp = self.time if self.time else timestamp
    mt = GetMainToken(self.token, timestamp)
    
    key = TH.config()
    OpenWith('Chrome', TH.server() + "/t/" + key + "/" + mt + "/" + timestamp + "/phones")
    return

  def OnMessages(self, event):
    self.token = GetToken()
    if self.token is None:
      wx.MessageBox(u'请先正确接入终端！', u'提示')
      return False
    
    timestamp = str(int(round(time.time() * 1000)))
    timestamp = self.time if self.time else timestamp
    mt = GetMainToken(self.token, timestamp)
    
    key = TH.config()
    OpenWith('Chrome', TH.server() + "/t/" + key + "/" + mt + "/" + timestamp + "/msgs")
    return

  def OnRegister(self, event):      
    if self.stStation.GetLabel():
      m = wx.MessageDialog(self, u'该终端已接入，是否变更？', u'提示', wx.YES_NO)
      answer = m.ShowModal()
      if answer == wx.ID_YES:
        d = RegisterDialog(self)
        d.ShowModal()
        d.Destroy()
      else:
        return

    else:
      d = RegisterDialog(self)
      d.ShowModal()
      d.Destroy()

  def OnCheckin(self, event):
    self.token = GetToken()
    if self.token is None:
      wx.MessageBox(u'请先正确接入终端！', u'提示')
      return False

    d = CheckinDialog(self)
    d.ShowModal()
    d.Destroy()

class MyApp(wx.App):
  def OnInit(self):
    self.name = "TydApp-%s" % wx.GetUserId()
    self.instance = wx.SingleInstanceChecker(self.name)
    if self.instance.IsAnotherRunning():
      wx.MessageBox(u'已经运行一个程序啦', u'出错提示')
      return False

    frame = TydMainFrame(None, -1, u'统一桌面')
    frame.Show(True)
    frame.Centre()
    return True

app = MyApp(0)
app.MainLoop()