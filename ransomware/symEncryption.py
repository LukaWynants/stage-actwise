from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
from keygen import *


class Symmetric_encryption:
    """
    a class which generates an AES key in memory
    """

    def __init__(self):
        self.AES_key = ""
        self.iv = ""

    def generate_key(self):
        """
        a function that generates an random 16 byte (128 bit) string to use as unique AES key and an initialization vector
        
        """
        self.AES_key = get_random_bytes(16) #create random strings as AES key
        self.iv = get_random_bytes(16) #create initialization vector 
         
        print(f"[INFO] KEY: {self.AES_key}")

    def encrypt_string(self, plain_text):
        """
        a function which encrypts plain text
        """
        #plain_text_bytes = plain_text.encode('utf-8')
        padded_data = pad(plain_text, AES.block_size) #pad the data to be a multiple of 16

        
        cipher = AES.new(self.AES_key, AES.MODE_CBC, self.iv) #create AES cipher object using CBC mode

        cipher_text = cipher.encrypt(padded_data) #encrypt the padded text

        #print(f"Encrypted data: {cipher_text}")
        
        return cipher_text

    def decrypt_string(self, cipher_text):
        decipher = AES.new(self.AES_key, AES.MODE_CBC, self.iv)
        decrypted_data = unpad(decipher.decrypt(cipher_text), AES.block_size)
        print(f"Decrypted data: {decrypted_data}")


if __name__=="__main__":

    symmetric_encryption = Symmetric_encryption()
    symmetric_encryption.generate_key()
    cipher_text = symmetric_encryption.encrypt_string("test")

    symmetric_encryption.decrypt_string(cipher_text)

