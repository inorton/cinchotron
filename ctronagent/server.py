"""
The base server implmentation for Cinchotron's agent

This provides a simple REST service we can use to instruct the agent
to do things or return console outputs.
"""
import os
import threading
import uuid

import jobthread
from control import ControllerJob
from ctronagent.agenthandler import CinchHTTPRequestHandler
from ctronlibs.webserver import ThreadedHTTPServer, CinchHTTPBaseServer

WORKSPACE = "ws"


class AgentHTTPServer(CinchHTTPBaseServer):
    def __init__(self, port=8989, sslkey=None, sslcert=None, wd=os.getcwd()):
        super(AgentHTTPServer, self).__init__(port, sslkey, sslcert, wd)
        self.controller = ControllerJob()
        self.jobthreads = dict()
        self.httpd = ThreadedHTTPServer(("0.0.0.0", port),
                                        CinchHTTPRequestHandler,
                                        self)

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
        super(AgentHTTPServer, self).start()

    def stop(self):
        """
        Stop the service
        :return:
        """
        super(AgentHTTPServer, self).stop()
        self.controller.stop()


if __name__ == "__main__":
    srv = AgentHTTPServer()
    srv.start()
    srv.wait()

