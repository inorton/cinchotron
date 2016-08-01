import SimpleHTTPServer
import errno
import socket
import json


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

    def json_respond(self, message, strio):
        """
        Send a JSON message response
        :param message: message to serialize
        :param strio: a StringIO() object
        :return:
        """
        strio.write(json.dumps(message))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", strio.tell())

    def send_head(self):
        """
        Dispatch GET requests.
        :return:
        """

        return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

