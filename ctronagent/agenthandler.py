import SimpleHTTPServer
import errno
import socket


class CinchHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    Handle HTTP Requests against this agent
    """
    def __init__(self, request, client_address, server):
        self.query = None
        self.path = None
        try:
            SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self,
                                                               request,
                                                               client_address,
                                                               server)
        except OSError as ose:
            if ose.errno == errno.EPIPE:
                pass
            raise
        except socket.error:
            pass
