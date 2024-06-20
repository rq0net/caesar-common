import uuid
import socket
from contextvars import ContextVar

_request_ctx = ContextVar('current_request', default={})

def get_current_request():
    return _request_ctx.get()


def set_current_request(new_context):
    # Set or update the current request context
    _request_ctx.set(new_context)


def add_to_request_context(key, value):
    # Add a new key-value pair to the current request context
    context = _request_ctx.get()
    context[key] = value
    _request_ctx.set(context)


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        return ip_address
    except OSError:
        return None

class ChangeLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        set_current_request({'request': request})

         # Add new data to the context
        add_to_request_context('request_id', str(uuid.uuid4()))
        add_to_request_context('ip_address', get_ip_address())

        response = self.get_response(request)
        return response
