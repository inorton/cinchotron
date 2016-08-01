"""
The job controller for an agent instance.
"""
import time
from jobthread import Job
import shutil


class ControllerJob(Job):
    """
    The first job an agent runs, it can be asked to spawn other jobs.
    """
    def __init__(self):
        super(ControllerJob, self).__init__()
        self.stop = False

    def start(self, args, cwd=None, envs=None):
        """
        Start the manager job.
        :param args:
        :param cwd:
        :param envs:
        :return:
        """
        self.workdir = cwd
        while not self.stop:
            time.sleep(10)

    def ended(self):
        """
        Called when the agent is shutting down
        :return:
        """
        shutil.rmtree(self.workdir)

    def stop(self):
        """
        Stop the manger job
        :return:
        """
        self.stop = True
        # now go through the server's jobs and tell them all to stop
        for job in self.server.jobthreads:
            job.stop()
