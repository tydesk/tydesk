def find_chrome_win():
  import winreg as reg
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
  import winreg as reg
  reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe'

  for install_type in reg.HKEY_LOCAL_MACHINE, reg.HKEY_CURRENT_USER:
    try:
      reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
      firefox_path = reg.QueryValue(reg_key, None)
      reg_key.Close()
    except WindowsError:
      pass

  return firefox_path