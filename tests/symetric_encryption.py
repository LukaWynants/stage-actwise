from Crypto.Cipher import AES
import os


class symmetric_encryption:

    def __init__(self):
        self.AES_key = ""

    def generate_key(self):
        """
        a function that generates an random 16 byte (128 bit) string to use as unique AES key
        
        """
        self.AES_key = os.urandom(16)
         
        print(f"[INFO] KEY: {self.AES_key}")

    def encrypt_string(self):
        
        cipher = AES.new(self.AES_key, AES.MODE_EAX, nonce=5)

    

        