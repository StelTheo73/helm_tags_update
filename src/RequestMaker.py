# Python Libraries
from inspect import stack
import requests
from requests.adapters import HTTPAdapter, Retry

# Program Libraries
from src.exceptions import (
    RequestFailedException,
    FetchInfoFailedException,
)
from src.contants import (
    GET,
    OK    
)
from src.utils import write_text_to_file


class RequestMaker(requests.Session):
    def __init__(self):
        super().__init__()
        self.status_forcelist = [429, 500, 502, 503, 504]
        self.backoff_factor = 0.1

    def set_status_forcelist(self, status_forcelist):
        self.status_forcelist = status_forcelist
    
    def set_backoff_factor(self, backoff_factor):
        self.backoff_factor = backoff_factor

    def make_request(self, uri, method=GET, timeout = 4, retries = 20):
        retries = Retry(total = retries,
                        backoff_factor = self.backoff_factor,
                        status_forcelist = self.status_forcelist
                    )
        adapter = HTTPAdapter(max_retries = retries)
        self.mount("https://", adapter)
        self.mount("http://", adapter)

        try:
            request_method = getattr(self, method.lower())
            write_text_to_file("Performing request to {} ...\n".format(uri), "execution.log", mode = "a")
            #print("Performing request to {} ...".format(uri))
            
            response = request_method(uri, timeout = timeout)
        except Exception as exc:
            raise RequestFailedException("make_request", exc.__str__(), uri)

        return response

    def _make_request(self, uri, headers = None, method = GET, timeout = 4, retries = 10):
        """Executes make_request inside a try/except block.
        
        Arguments:

        Returns:

        Raises:

        """
        write_text_to_file("{} -> {}\n".format(stack()[2].function, stack()[1].function), "execution.log", mode = "a")
        try:
            response = self.make_request(uri, method, timeout, retries)

            if response.status_code != OK:
                caller = stack()[0].function
                msg = "Response status code was: {}.".format(response.status_code)
                raise FetchInfoFailedException(caller, msg)

        except RequestFailedException:
            caller = stack()[0].function
            msg = "RequestFailedException was raised."
            raise   FetchInfoFailedException(caller, msg)

        return response
    
    def validate_uri(self, uri):
        pass
