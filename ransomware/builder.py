import base64

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

    def decode(self):
        """
        a method to decode base64
        """
        
        base64_bytes = self.encoded_code.encode("ascii")

        encoded_code_bytes = base64.b64decode(base64_bytes)
        sample_string = encoded_code_bytes.decode("ascii")

        print(f"Decoded string: {sample_string}")



if __name__ == "__main__":
    encodeclass = Encode()
    
    with open("encryptor.py", "r") as malicious_payload:
        payload = malicious_payload.read()
        encoded_payload = encodeclass.encode(payload)

    with open("encoded_code.txt", "w") as text_file:
        text_file.write(encoded_payload)