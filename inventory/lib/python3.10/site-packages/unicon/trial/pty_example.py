import pty
import os
import sys
import select
import signal
import time
import re
from unicon.settings import Settings
from unicon.eal.utils import ExpectMatch, Timer
from unicon.core.errors import TimeoutError

from unicon import log
command = "/Users/vivejha/Projects/cisco/src/cisco-shared/unicon/docs/examples/router.sh"

# pid, fd = pty.fork()

# if pid == 0:
#     say('+++ inside child process +++')
#     try:
# os.execvp(command, ['e'])
#         os.system(command)
#     except Exception as err:
#         say(err)
#         raise

# else:
#     say("+++ inside parent process +++")
#     fhw = os.fdopen(fd, 'w')
#     fhr = os.fdopen(os.dup(fd), 'r')


class Spawn():

    def __init__(self, spawn_command,
                 log=log,
                 session=None,
                 size=None,
                 log_user=None,
                 timeout=None,
                 internal_logs=False,
                 invoke_shell_timeout=None,
                 proxy_prompt_pattern=None,
                 settings=Settings()
                 ):
        self.size = size or settings.SIZE
        self.log = log
        self.log_user = log_user or settings.LOG_USER
        self.timeout = timeout or settings.EXPECT_TIMEOUT
        self.internal_logs = internal_logs
        self.last_sent = spawn_command
        self.buffer = ""
        self.settings = settings
        self.FLAG = True
        self.match = ExpectMatch()

        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            try:
                # os.execvp(command, ['e'])
                os.system(spawn_command)
            except Exception as err:
                sys.stdout.write(str(err))
                sys.exit(1)

    def send(self, command, *args, **kwargs):
        if self.is_writable():
            self.log.info("sending : %s" % repr(command))
            return os.write(self.fd, str.encode(command))
        else:
            return False

    def sendline(self, command=None):
        if command is None:
            command = ""
        # command = "" if command is None else command
        self.send(command + "\r")

    def read(self, size=None):
        size = size or self.size
        if self.is_readable():
            return os.read(self.fd, size).decode('utf-8')
        else:
            return None

    def read_update_buffer(self, size=None):
        """perform a single read and update buffer content"""
        size = size or self.size
        if self.is_readable():
            data = self.read()
            self.buffer += data
            return True
        else:
            time.sleep(0.01)

        return True if self.FLAG else False

    def match_buffer(self, pat_list):
        if isinstance(pat_list, str):
            pat_list = [pat_list]
        for idx, pattern in enumerate(pat_list):
            match = re.search(pattern, self.buffer, re.DOTALL)
            if match:
                self.match.last_match = match
                self.match.match_output = match.group()
                return idx

        self.FLAG = False
        return False

    def trim_buffer(self):
        """trims the buffer based on match object"""
        if self.match.last_match:
            matched_data = self.buffer[:self.match.last_match.end()]
            self.buffer = self.buffer[self.match.last_match.end():]
            if self.buffer != '':
                self.FLAG = True
            return True
        return False

    def is_readable(self, timeout=0.01):
        r, w, e = select.select([self.fd], [], [], timeout)
        return True if self.fd in r else False

    def is_writable(self, timeout=0.01):
        r, w, e = select.select([], [self.fd], [], timeout)
        return True if self.fd in w else False

    def expect(self, patterns,
               timeout=None,
               size=None,
               trim_buffer=True):
        """match a list of patterns against the buffer

        expect takes a list of patterns and matches it against the content of
        the buffer. After any one of the patterns matches, in the user provided
        list, it trims the buffer till that match. The buffer contains the
        remaining data in an anticipation that it will be used in the expect
        call for matching.

        However sometime it may be useful to maintain the buffer as it is, even
        after the match has happened. This is equivalent to the no_transfer
        feature in the Tcl/Expect. To achieve that effect trim_buffer can be
        set to False, which is True by default.

        Args:
            patterns: list of patterns.
            timeout: time to wait for any of the patterns to match.
            size: read size in bytes for reading the buffer.
            trim_buffer: whether to trim the buffer after a successful match.

        Example:
            ::

                e.sendline("a command")
                e.expect([r'^pat1', r'pat2'], timeout=10)

        Returns:
            ExpectMatch instance.
            * It contains the index of the pattern that matched.
            * matched string.
            * re match object.

        Raises:
            TimeoutError: In case no match is found within the timeout period.

        """
        # reset the match
        self.match = ExpectMatch()
        timeout = timeout or self.timeout
        size = size or self.size

        timer = Timer(timeout)
        timer.start()
        while True:
            if timer.has_time_left():
                # if there was a data in the channel
                if self.read_update_buffer():
                    idx = self.match_buffer(patterns)
                    # in case there is a match, prepare for exit
                    if idx is not False:
                        # trim the buffer if it is True and match is found
                        if trim_buffer:
                            self.trim_buffer()
                        else:
                            self.FLAG = True
                        return self.match
            else:
                raise TimeoutError('Timeout occurred')

    def close(self):
        os.kill(self.pid, signal.SIGKILL)

if __name__ == '__main__':
    s = Spawn(command)
    s.sendline()
    s.expect("nopattern", timeout=10)
