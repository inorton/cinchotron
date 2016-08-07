import threading
import ssl
import os
import time

from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __init__(self, listen, handler, cinchserver):
        HTTPServer.__init__(self, listen, handler)
        self.cinchserver = cinchserver


class CinchHTTPBaseServer(object):
    """
    Common base class for all Cinchotron web servers
    """
    def __init__(self, port=8989, sslkey=None, sslcert=None, wd=os.getcwd()):
        self.initialdir = wd
        self.port = port
        self.sslkey = sslkey
        self.sslcert = sslcert
        self.serverthread = None
        self.lck = threading.Lock()
        self.stop = False
        self.httpd = None

    def setup_ssl(self):
        """
        Load our ssl key and wrap the server socket
        :return:
        """
        if self.sslkey:
            protocol = ssl.PROTOCOL_TLSv1
            if hasattr(ssl, "PROTOCOL_TLSv1_2"):
                protocol = getattr(ssl, "PROTOCOL_TLSv1_2")

            self.httpd.socket = ssl.wrap_socket(
                keyfile=self.sslkey, certfile=self.sslcert,
                server_side=True,
                ssl_version=protocol)

    def start(self):
        """
        Start the server in the background
        :return:
        """
        self.setup_ssl()
        self.serverthread = threading.Thread(target=self.httpd.serve_forever)
        self.serverthread.setDaemon(True)
        self.serverthread.start()

    def stop(self):
        """
        Stop the service
        :return:
        """
        self.httpd.shutdown()
        self.serverthread.join()

    def wait(self):
        """
        Wait for the server to exit
        :return:
        """
        while not self.stop:
            time.sleep(5)
