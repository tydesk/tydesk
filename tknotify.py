#!/usr/bin/env python
# Author: Willie Lawrence - cptx032@gmail.com

import sys
import tkFont
from Tkinter import *

def show(**kws):
	"""
	Attributes:
		title: the title message (in bold font)
		msg(opt):	the message
		expire_time(opt): how long the message will be showed (default 2000ms)
		spacing(opt): the distance to screen border (default 20)
		justify(opt): The title and msg justify (default 'left')
		text_padding(opt): The padding of title or msg (default 50)
		alpha(opt): The alpha of windows (default 1.0)
	"""
	title = kws.get("title")
	msg = kws.get("msg", False)
	expire_time = kws.get("expire_time", 4000)
	spacing = kws.get("spacing", 20)
	justify = kws.get("justify", CENTER)
	text_padding = kws.get("text_padding", 50)
	alpha = kws.get("alpha", 1.0)

	top = Toplevel()
	top.attributes("-alpha", alpha)
	TITLE_FONT = tkFont.Font(size=36,family="TkDefaultFont",weight=tkFont.BOLD)
	MSG_FONT = tkFont.Font(size=9,family="TkDefaultFont")
	top.withdraw()
	top.attributes("-topmost", 1)
	top.overrideredirect(True)
	top.config(bd=0,highlightthickness=0,bg="#990000")
	Label(top,text=title,fg="#fff",bd=0,
		highlightthickness=0,justify=justify,font=TITLE_FONT,
		bg=top["bg"]).pack(expand=YES,fill=BOTH)
	if msg:
		Label(top,text=msg,fg="#fff",bd=0,
			highlightthickness=0,justify=justify,font=MSG_FONT,
			bg=top["bg"]).pack(expand=YES,fill=BOTH)
	top.update_idletasks()
	SW = top.winfo_screenwidth() # screen width
	WW = TITLE_FONT.measure(title)
	if msg and MSG_FONT.measure(msg) > WW:
		WW = MSG_FONT.measure(msg)
	WW += text_padding
	qt_lines_title = len(title.split("\n"))
	WH = qt_lines_title * TITLE_FONT.metrics().get("ascent")
	WH += (qt_lines_title-1)*TITLE_FONT.metrics().get("linespace")
	if WH < 50:
		WH = 50
	top.geometry("%dx%d+%d+%d" % (WW,WH,SW-WW-spacing,spacing))
	top.after(expire_time, top.destroy)
	top.deiconify()