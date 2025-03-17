import win32con as con
import win32api
import ntsecuritycon as ntc
import pywintypes
import win32security

# Correct registry path (no leading 'HKEY_LOCAL_MACHINE')
key = win32api.RegOpenKey(con.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows Defender\Features', 0, con.KEY_ALL_ACCESS)
ksd = win32api.RegGetKeySecurity(key, con.DACL_SECURITY_INFORMATION)

acl = pywintypes.ACL()
acl.AddAccessAllowedAce(ntc.GENERIC_ALL, win32security.ConvertStringSidToSid('S-1-5-18'))  # SYSTEM
acl.AddAccessAllowedAce(ntc.GENERIC_ALL, win32security.ConvertStringSidToSid('S-1-5-32-544'))  # Administrators

ksd.SetDacl(True, acl, False)

win32api.RegSetKeySecurity(key, con.DACL_SECURITY_INFORMATION, ksd)
