"""
The base server implmentation for Cinchotron's agent

This provides a simple REST service we can use to instruct the agent
to do things or return console outputs.
"""
import os
import ssl
import threading
import time
import uuid
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

import jobthread
from control import ControllerJob
from ctronagent.agenthandler import CinchHTTPRequestHandler

WORKSPACE = "ws"


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __init__(self, listen, handler, cinchserver):
        HTTPServer.__init__(self, listen, handler)
        self.cinchserver = cinchserver


class CinchAgentServer(object):
    def __init__(self, port=8989, sslkey=None, sslcert=None, wd=os.getcwd()):
        self.initialdir = wd
        self.port = port
        self.sslkey = sslkey
        self.sslcert = sslcert
        self.serverthread = None
        self.controller = ControllerJob()
        self.jobthreads = dict()
        self.lck = threading.Lock()
        self.stop = False
        self.httpd = ThreadedHTTPServer(("0.0.0.0", port),
                                        CinchHTTPRequestHandler,
                                        self)
        if sslkey:
            protocol = ssl.PROTOCOL_TLSv1
            if hasattr(ssl, "PROTOCOL_TLSv1_2"):
                protocol = getattr(ssl, "PROTOCOL_TLSv1_2")

            self.httpd.socket = ssl.wrap_socket(
                keyfile=sslkey, certfile=sslcert,
                server_side=True,
                ssl_version=protocol)

    def get_temp_prefix(self):
        """
        Return a prefix jobs can use with tempfile.mkdtemp()
        :return:
        """
        wsdir = os.path.join(self.initialdir, WORKSPACE)
        if not os.path.exists(wsdir):
            os.makedirs(wsdir)
        return wsdir

    def add_job(self, job, args, envs, newid=None):
        """
        Add a job to this server and start it
        :param job: the job object
        :param args: arguments for this job
        :param envs: an environment dictionary if required
        :param newid: An ID for the job, if omitted a unique string is generated
        :return:
        """
        if newid is None:
            newid = str(uuid.uuid4())

        assert isinstance(job, jobthread.Job)

        job.setup(self, newid)
        jthread = threading.Thread(target=jobthread.begin,
                                   args=(job, args, envs))
        jthread.setDaemon(True)
        jthread.start()
        with self.lck:
            self.jobthreads[newid] = jthread

    def start(self):
        """
        Start the server in the background
        :return:
        """
        self.add_job(self.controller, None, None, "controller")
        self.serverthread = threading.Thread(target=self.httpd.serve_forever)
        self.serverthread.setDaemon(True)
        self.serverthread.start()

    def stop(self):
        """
        Stop the service
        :return:
        """
        self.controller.stop()
        self.httpd.shutdown()
        self.serverthread.join()

    def wait(self):
        """
        Wait for the server to exit
        :return:
        """
        while not self.stop:
            time.sleep(5)


if __name__ == "__main__":
    srv = CinchAgentServer()
    srv.start()
    srv.wait()

