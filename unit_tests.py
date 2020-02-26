"""
Author: Assaf Bentabou
Data: 24/02/20

Unit-tests for client and server.
"""

import unittest
from client import PingClient
from server import PingServer
import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def captured_output():
    """
    Gets the latest output that was sent to stdout.
    :return: Next stdout output.
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestServer(unittest.TestCase):
    def test_tcp_connection(self):
        ping_server = PingServer(port=80,
                                 response_buffer_size=1024,
                                 hostname="localhost")

        # Start server up and log output.
        with captured_output() as (server_out, server_err):
            ping_server.start()

        ping_client = PingClient(target_name="localhost",
                                 count=4,
                                 continuous=False,
                                 size=32,
                                 timeout=4000,
                                 l4_protocol="TCP",
                                 port=80,
                                 response_buffer_size=1024)

        ping_client.ping()

        # Get server's output after being pinged.
        output = server_out.getvalue().strip()

        # TODO: Assertion.

    def test_udp_connection(self):
        pass

    def test_connection_from_non_default_port(self):
        pass

    def test_big_size_ping(self):
        pass


class TestClient(unittest.TestCase):
    def test_continuous_mode(self):
        pass

    def test_big_size_ping(self):
        pass

    def test_short_timeout(self):
        pass

    def test_long_timeout(self):
        pass

    def test_tcp_connection(self):
        pass

    def test_udp_connection(self):
        pass

    def test_connection_from_non_default_port(self):
        pass


if __name__ == '__main__':
    # Explicit list to unittest.main will prevent looking at sys.argv.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
