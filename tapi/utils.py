from werkzeug.datastructures import Headers
from tapi.constants import *


def add_mason_request_header(h=None):
    if h is None:
        h = Headers()
    h.add('Content-Type', CONTENT_TYPE_MASON)
    return h
