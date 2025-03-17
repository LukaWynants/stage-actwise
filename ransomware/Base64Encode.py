import base64

class Encode:

    def __init__(self):
        self.file = ""
        self.encoded_code = ""

    

    def read_file(self):

        with open(self.file, 'r') as file:
            file.read()

    def encode(self, code):
        code_bytes = code.encode("ascii")
        base64_bytes = base64.b64encode(code_bytes)
        base64_string = base64_bytes.decode("ascii")
        print(f"Encoded string: {base64_string}")

        return base64_string

    def decode(self):
        
        
        base64_bytes = self.encoded_code.encode("ascii")

        encoded_code_bytes = base64.b64decode(base64_bytes)
        sample_string = encoded_code_bytes.decode("ascii")

        print(f"Decoded string: {sample_string}")

encodeclass = Encode()

encoded_str = "test"



