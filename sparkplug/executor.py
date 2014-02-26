import os
import errno
import select
import signal
import socket
import sys
import time
import contextlib as cx

import sparkplug.logutils

_log = sparkplug.logutils.LazyLogger(__name__)

def always(*connections):
    return True

def direct(f):
    """Runs a task in the current process. This is a very thin wrapper around
    a direct function call."""
    return f(always)

class Subprocess(object):
    """Runs a task in N subprocesses. The current process is suspended (using
    ``wait``) until a signal arrives or a child process exits."""
    
    def __init__(self, process_count):
        self.process_count = process_count
        self.continuing = True
        self.workers = set()
        self.parent_socket, self.child_socket = socket.socketpair()
    
    def parent_surviving(self, *connections):
        timeout = None
        if len(connections) == 0:
            # If there are no open connections, then poll instead of blocking
            # so that workers can continue onwards and open a connection.
            # They'll return to this check (with a connection) as soon as
            # they've done so.
            timeout = 0
        elif any(len(connection.method_queue) > 0 for connection in connections):
            # If any connection has unprocessed data from the server in its
            # queue, poll instead of blocking so that the worker can process
            # that data without waiting for further IO to tickle the select.
            # The worker will return to this check (with an empty queue) as
            # soon as it's done so.
            timeout = 0
        elif any(
            len(getattr(connection.transport, '_read_buffer', bytes())) > 0
            for connection in connections
        ):
            # The amqplib `TCPTransport` class internally buffers data read
            # ahead of the current message. If this buffer is non-empty, poll
            # instead of blocking so that the worker can process that data
            # without waiting for further IO to tickle the select. The worker
            # will return to this check (with an empty buffer) as soon as
            # it's done so.
            timeout = 0
        sockets = [conn.transport.sock for conn in connections] + [self.child_socket]
        read, write, exception = select.select(sockets, [], [], timeout)
        if self.child_socket in read:
            _log.debug("Master process has died; exiting")
        return self.child_socket not in read
    
    def __call__(self, f):
        try:
            with self.register_shutdown_signals() as default_handlers:
                while self.continuing:
                    self.start_workers(default_handlers, f)
                    self.await_worker()
        finally:
            self.terminate_workers()

    def start_workers(self, default_handlers, f):
        while len(self.workers) < self.process_count:
            self.start_worker(default_handlers, f)

    def start_worker(self, default_handlers, f, *args, **kwargs):
        import pysigset as sigset
        # Suspend signals related to this fork manager, so that we don't do
        # dumb things like set self.continuing = False in the child process
        # when we should actually be shutting down or crashing.
        sigsuspend = sigset.suspended_signals(*default_handlers.keys())
        with sigsuspend:
            pid = os.fork()
            if pid == 0:
                self.handle_signals(default_handlers)
                # reinstate signals; we will never exit the context manager
                # normally in this process, so invoke it directly.
                sigsuspend.__exit__(None, None, None)
                self.abandon_stdin()
                self.abandon_parent()
                try:
                    f(self.parent_surviving)
                finally:
                    # skip the rest of sparkplug shutdown, in worker processes
                    # only
                    os._exit(0)
            else:
                self.workers.add(pid)
        # Only reachable on parent process. Do not do log IO inside sigsuspend
        # critical section unless you want uninterruptible IO!
        assert pid != 0
        _log.debug("Started worker (pid %d)", pid)

    def abandon_stdin(self):
        sys.stdin.close()

    def abandon_parent(self):
        self.parent_socket.close()

    def await_worker(self):
        try:
            pid, status = os.wait()
            self.workers.remove(pid)
            _log.warn("Worker (pid %d) exited unexpectedly with status %s", pid, status)
        except OSError as e:
            # signal handling will set self.continuing = False for EINTR
            if e.errno != errno.EINTR:
                raise

    def terminate_workers(self):
        self.parent_socket.close()
        for worker in self.workers:
            _log.debug("Signalling worker (pid %d)", worker)
            os.kill(worker, signal.SIGINT)
            os.waitpid(worker, 0)

    @cx.contextmanager
    def register_shutdown_signals(self):
        original_handlers = self.handle_signals({
            signal.SIGINT: self.stop,
            signal.SIGTERM: self.stop,
        })
        try:
            yield original_handlers
        finally:
            self.handle_signals(original_handlers)

    def handle_signals(self, handlers):
        import pysigset as sigset
        original_handlers = {}
        # This can be called inside of another suspended_signals guard,
        # inside of start_worker. This is "safe" -- exiting the inner
        # suspended_signals guard reinstates the outer guard, provided
        # nothing directly manipulates the signal mask in the interim.
        with sigset.suspended_signals(*handlers.keys()):
            for sig_number in handlers:
                original_handlers[sig_number] = signal.signal(sig_number, handlers[sig_number])
        return original_handlers

    def stop(self, _signal=None, _frame=None):
        """Arrange for execution to stop as soon as possible. The actual work
        termination won't actually happen until ``__call__`` next returns from
        ``os.wait``, which will be immediate if this is called from inside a
        signal handler.

        This method can be called as a signal handler, or directly as
        ``stop()``.
        """
        self.continuing = False
