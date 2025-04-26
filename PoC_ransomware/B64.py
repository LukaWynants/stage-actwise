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
        #code_bytes = code.encode("ascii")
        base64_bytes = base64.b64encode(code)
        base64_string = base64_bytes.decode("ascii")
        #print(f"Encoded string: {base64_string}")

        return base64_string

    def decode(self, encoded_code):
        """
        a method to decode base64
        """

        encoded_code_bytes = base64.b64decode(encoded_code)

        return encoded_code_bytes
