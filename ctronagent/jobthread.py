"""
A thread and container for a single ongoing operation.
"""

import time
import os
import subprocess
from ctronlibs import tempfolder


def begin(job, args, envs):
    """
    Thread body for starting a job
    :param job:
    :param args:
    :param envs:
    :return:
    """
    workspace_prefix = job.server.get_temp_prefix()
    with tempfolder.gashdir(workspace_prefix) as workdir:
        try:
            job.start(cwd=workdir, args=args, envs=envs)
        finally:
            # perhaps the job will clean up after itself or upload some logs
            job.ended()


class Job(object):
    """
    A single potentially long running operation
    :return:
    """

    CHILD_LOGFILE = "stdio.log"

    def __init__(self):
        """
        Create a job object
        :return:
        """
        self.description = "Base CI Job"
        self.server = None
        self.id = None
        self.child = None
        self.workdir = None

    def setup(self, server, jobid):
        """
        Prepare the job for work
        :param server: the server hosting us
        :param jobid: our unique id string
        :return:
        """
        self.server = server
        self.id = jobid

    def start(self, args, cwd=None, envs=None):
        """
        Start the job
        :param args: 
        :param cwd: 
        :param envs: 
        :return: 
        """
        raise NotImplementedError()

    def ended(self):
        """
        Called after the start method has finished.
        :return:
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop this job as soon as possible.
        :return:
        """
        raise NotImplementedError()


class SubprocessJob(Job):
    """
    A job that wraps a single long running child process
    """
    def __init__(self):
        super(SubprocessJob, self).__init__()

    def open_child_log(self):
        """
        Return a file object for the child's log
        :return:
        """
        return open(os.path.join(self.workdir, Job.CHILD_LOGFILE), "wb")

    def start(self, args, cwd=None, envs=None):
        """
        Start a sub process, pipe it's stdout/stderr into a log file.
        Block until the child exits.

        stderr and stdout are combined
        :param args: the command line to execute
        :param cwd: the initial directory
        :param envs: a dictionary of environment variables
        :return:
        """
        self.description = "Subprocess Job: {}".format(str(args))
        self.workdir = cwd
        with self.open_child_log() as logs:
            try:
                self.child = subprocess.Popen(args,
                                              env=envs,
                                              cwd=cwd,
                                              shell=False,
                                              stdout=logs,
                                              stderr=subprocess.STDOUT)
                while self.child.poll() is None:
                    time.sleep(5)
                return self.child.returncode

            except Exception as err:
                print "" > logs
                print "-" * 80 >> logs
                print str(err) >> logs
                raise

    def ended(self):
        """
        The child finished or was terminated.
        :return:
        """
        pass

    def stop(self):
        """
        Stop the child now
        :return:
        """
        if self.child:
            if self.child.poll() is not None:
                self.child.terminate()
