from utils import write_text_to_file

class BaseTracerException(Exception):
    def __init__(self, exception_name, method_name, msg):
        self.exception_name = exception_name
        self.method_name = method_name
        self.msg = msg

        self.message = "\n{} (from {}):\n\
            {}".format(self.exception_name, self.method_name, self.msg)
        print(self.message)
        write_text_to_file(self.message, "err.log", mode="a")
        
    def __str__(self):
        return self.message 

class RequestFailedException(BaseTracerException):
    def __init__(self, method_name, msg, uri):
        exc_msg =  "Request to {} failed due to: {}".format(uri, msg)
        super().__init__("RequestFailedException", method_name, exc_msg)

    def __str__(self):
        return super().__str__()

class FetchInfoFailedException(BaseTracerException):
    def __init__(self, method_name, msg):
        exc_msg = "Fetch failed due to: {}".format(msg)
        super().__init__("FetchInfoFailedException", method_name, exc_msg)

    def __str__(self):
        return super().__str__()

class ElementNotFoundException(BaseTracerException):
    def __init__(self, method_name, element):
        exc_msg = "Element \"{}\" not found.".format(element)
        super().__init__("ElementNotFoundException", method_name, exc_msg)

    def __str__(self):
        return super().__str__()

class BranchNotFoundException(BaseTracerException):
    def __init__(self, method_name, branch_name, msg):
        exc_msg = "Branch \"{}\" not found. Failed due to: {}".format(branch_name, msg)
        super().__init__("BranchNotFoundException", method_name, exc_msg)

    def __str__(self):
        return super().__str__()

class PathNotFoundException(BaseTracerException):
    def __init__(self, method_name, path):
        exc_msg = "Path \"{}\" not found.".format(path)
        super().__init__("PathNotFoundException", method_name, exc_msg)

    def __str__(self):
        return super().__str__()