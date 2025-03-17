import os
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    script = sys.argv[0]
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)

if not is_admin():
    print("Dit script vereist administratorrechten.")
    run_as_admin()
    sys.exit(0)

# Code voor schaduwkopieën verwijderen (bijv.)
print("Administratorrechten verkregen, voer hier je functie uit.")