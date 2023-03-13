"""This module defines exceptions."""

# Program Libraries
from src.constants import (
    EXECUTION_LOG_FILE,
    ERROR_LOG_FILE
)
from src.utils import write_text_to_file

class BaseTracerException(Exception):

    """Base class for most of exceptions, creates error logs."""

    def __init__(self, exception_name, method_name, msg):
        self.exception_name = exception_name
        self.method_name = method_name
        self.msg = msg

        self.message = f"{self.exception_name} (from {self.method_name}):\n    {self.msg}\n"

        write_text_to_file(self.message, EXECUTION_LOG_FILE, mode = "a")
        write_text_to_file(self.message, ERROR_LOG_FILE, mode="a")

    def __str__(self):
        return self.message

class InvalidUriException(BaseTracerException):

    """Exception for the cases where the given URI is invalid."""

    def __init__(self, method_name, uri):
        exc_msg = f"Uri {uri} is invalid."
        super().__init__("InvalidUriException", method_name, exc_msg)

class RequestFailedException(BaseTracerException):

    """Exception for the cases where the HTTP request has failed."""

    def __init__(self, method_name, msg, uri):
        exc_msg =  f"Request to {uri} failed due to: {msg}"
        super().__init__("RequestFailedException", method_name, exc_msg)

class FetchInfoFailedException(BaseTracerException):

    """Exception for the cases where fetching info from gitlab has failed."""    

    def __init__(self, method_name, msg):
        exc_msg = f"Fetch failed due to: {msg}"
        super().__init__("FetchInfoFailedException", method_name, exc_msg)

class ElementNotFoundException(BaseTracerException):

    """Exception for the cases an element was not found in a dict."""

    def __init__(self, method_name, element):
        exc_msg = f"Element \"{element}\" not found."
        super().__init__("ElementNotFoundException", method_name, exc_msg)

class BranchNotFoundException(BaseTracerException):

    """Exception for the cases the specified branch was not found on gitlab."""

    def __init__(self, method_name, branch_name, msg):
        exc_msg = f"Branch \"{branch_name}\" not found. Failed due to: {msg}"
        super().__init__("BranchNotFoundException", method_name, exc_msg)
