"""HTTP Request Maker."""

# Python Libraries
from inspect import stack
import json
import re
import requests
from requests.adapters import HTTPAdapter, Retry
from halo import Halo

# Program Libraries
from src.constants import (
    GET,
    OK,
    EXECUTION_LOG_FILE
)
from src.exceptions import (
    FetchInfoFailedException,
    InvalidUriException,
    RequestFailedException
)
from src.utils import write_text_to_file


class RequestMaker(requests.Session):
    """The RequestMaker class is a subclass of requests.Session
    and is responsible for making HTTP requests."""

    def __init__(self):
        """Instantiates a RequestMaker object.

        Initializes status_forcelist (for which HTTP status codes
        a retry should be performed) and backoff_factor between retries.
        
        Returns:
            (RequestMaker object): The instantiated RequestMaker object.
        """
        super().__init__()
        # HTTP status codes for which a retry should be performed
        self.status_forcelist = [429, 500, 502, 503, 504]
        # A backoff factor to apply between attempts after the second try.
        self.backoff_factor = 0.1

    def set_status_forcelist(self, status_forcelist):
        """Sets the status_forcelist.
        
        Args:
            status_forcelist(list): A list of integers corresponding
                                    to the HTTP status codes for which
                                    a retry should be performed.

        """
        self.status_forcelist = status_forcelist

    def set_backoff_factor(self, backoff_factor):
        """Sets the backoff factor.

        Args:
            backoff_factor(float): A float number between 0 and 1.
        """
        self.backoff_factor = backoff_factor

    def make_request(self, uri, method=GET, timeout = 10, retries = 10):
        """Performs an HTTP request to a specified uri.
        
        Args:
            uri(string): The uri to which the request will be made.
            method(string): The HTTP method to be used (default is GET).
            timeout(int): Number of seconds the client waits to get a
                          response form the server (default is 10).
            retries(int): How many times the client will retry if there
                          is no response from the server or one of the codes
                          in status_forcelist is returned.

        Returns:
            (requests.models.Response object): The response from the server.

        Raises:
            InvalidUriException: If the provided uri is invalid.
            RequestFailedException: If the request failed for any reason.
        """

        retries = Retry(total = retries,
                        backoff_factor = self.backoff_factor,
                        status_forcelist = self.status_forcelist
                    )
        adapter = HTTPAdapter(max_retries = retries)
        self.mount("https://", adapter)
        self.mount("http://", adapter)

        if not self.validate_uri(uri):
            raise InvalidUriException(stack()[0], uri)

        try:
            request_method = getattr(self, method.lower())

            log_msg = f"Performing {method} request to {uri} ...\n"
            write_text_to_file(log_msg, EXECUTION_LOG_FILE, mode = "a")

            response = request_method(uri, timeout = timeout)
        except Exception as exc:
            raise RequestFailedException(stack()[0], str(exc), uri) from exc

        return response

    def make_request_and_expect_200(self, uri, method = GET, timeout = 10, retries = 10):
        """Executes make_request inside a try/except block 
        and verifies that status code is 200 - OK.

        Args:
            uri(string): The uri to which the request will be made.
            method(string): The HTTP method to be used (default is GET).
            timeout(int): Number of seconds the client waits to get a
                          response form the server (default is 10).
            retries(int): How many times the client will retry if there
                          is no response from the server or one of the codes
                          in status_forcelist is returned.

        Returns:
            (requests.models.Response object): The response from the server.

        Raises:
            FetchInfoFailedException: 
                - If status code of the response is not 200 - OK.
                - If RequestFailedException was raised from make_request.
        """
        log_msg = f"{stack()[2].function} -> {stack()[1].function}\n"
        write_text_to_file(log_msg, EXECUTION_LOG_FILE, mode = "a")
        try:
            response = self.make_request(uri, method, timeout, retries)

            if response.status_code != OK:
                caller = stack()[0].function
                msg = f"Response status code was: {response.status_code}."
                raise FetchInfoFailedException(caller, msg)

        except (RequestFailedException, InvalidUriException) as exc:
            caller = stack()[0].function
            msg = "RequestFailedException was raised."
            raise   FetchInfoFailedException(caller, msg) from exc

        return response

    def recursive_request(self, uri, deep_search = True, spinner_text = None):
        """Iteratively calls make_request_and_expect_200 until 
        the text of server's response is empty.

        """
        page_number = 1
        json_list = []

        while True:
            page_uri = uri.format(page_number = page_number)

            if (spinner_text is not None) and deep_search:
                _spinner_text = spinner_text + f" (page = {page_number})"
            else:
                _spinner_text = spinner_text

            response = self.make_request_and_display_spinner(page_uri, _spinner_text)

            if response.text in ["[]", ""]:
                break
            json_list += json.loads(response.text)

            if not deep_search:
                break

            page_number +=1

        return json_list

    def make_request_and_display_spinner(self, uri, spinner_text = None):
        """Executes make_request_and_expect_200 and display a spinner while waiting for response.

        Args:
            uri(string): The uri to which the request will be made.
            spinner_text: The text to be displayed next to the spinner.

        Returns:
            (requests.models.Response object): The response from the server.

        Raises:
            FetchInfoFailedException: 

        """
        spinner_text = f"Fetching {spinner_text}..."
        spinner = Halo(text = spinner_text, spinner = "dots")
        spinner.start()
        try:
            response = self.make_request_and_expect_200(uri)
        except FetchInfoFailedException as exc:
            spinner.fail(text = spinner_text)
            msg = str(exc)
            raise FetchInfoFailedException(stack()[0], msg) from exc

        spinner.succeed(text = spinner_text)
        return response

    def validate_uri(self, uri):
        """Validates the given uri.

        Args:
            uri(string): The uri to be validated.

        Returns:
            (boolean): True if the uri is valid, 
                       False otherwise.
        """

        uri_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
        if re.match(uri_pattern, uri):
            return True
        return False
