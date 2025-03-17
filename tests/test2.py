import winreg as reg
import os

def disable_defender_tamper_protection():
    try:
        # Path to Windows Defender Features registry settings
        reg_path = r"SOFTWARE\Microsoft\Windows Defender\Features"
        
        # Open the registry key with write access
        reg_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, reg_path, 0, reg.KEY_WRITE)
        
        # Set the TamperProtection DWORD value to 0 (disabled)
        reg.SetValueEx(reg_key, "TamperProtection", 0, reg.REG_DWORD, 0)
        print("Tamper Protection Disabled")
        
        # Close the registry key
        reg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error occurred: {str(e)}")


def main():

    disable_defender_tamper_protection()

if __name__ == "__main__":
    main()