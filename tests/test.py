import subprocess

def get_tamper_protection_status():
    """
    a command that retrieves information about tamper protection
    """
    command = "powershell (Get-MpComputerStatus).IsTamperProtected"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return f"Error: {result.stderr}"

status = get_tamper_protection_status()
print(f"tamper protection: {status}")