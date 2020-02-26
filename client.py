"""
Author: Assaf Bentabou
Data: 24/02/20

Client-server python script for "ping" over TCP or UDP.
"""

import argparse
import socket
from utils import create_data_string
import datetime


class PingClient:
    def __init__(self,
                 target_name,
                 count,
                 continuous,
                 size,
                 timeout,
                 l4_protocol,
                 port,
                 response_buffer_size):

        self.target_name = target_name
        self.count = count
        self.continuous = continuous
        self.size = size
        self.timeout = timeout
        self.l4_protocol = l4_protocol
        self.port = port
        self.response_buffer_size = response_buffer_size
        self._socket = None
        self._init_socket()

    def __exit__(self):
        self._socket.close()

    def _init_socket(self):
        """
        Initializes a new socket into 'self._socket', according to the requested protocol.
        :return: None
        """
        if self.l4_protocol == "TCP":
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.connect((self.target_name, self.port))
            except socket.error:
                print("Ping request could not find host {target_name}:{port}. Please check the name and try "
                      "again.".format(target_name=self.target_name,
                                      port=self.port))
                exit(0)

        elif self.l4_protocol == "UDP":
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                print("Ping request could not find host {target_name}:{port}. Please check the name and try "
                      "again.".format(target_name=self.target_name,
                                      port=self.port))
                exit(0)

    @staticmethod
    def _millis_interval(start_time, end_time):
        """
        Calculates the difference between 'end_time' - 'start_time' and converts it into milliseconds.
        :param start_time: datetime
        :param end_time: datetime
        :return: Time delta in milliseconds.
        """
        diff = end_time - start_time
        millis = diff.days * 24 * 60 * 60 * 1000
        millis += diff.seconds * 1000
        millis += diff.microseconds / 1000
        return millis

    def _plot_ping_statistics(self, time_delta_list, num_sent, num_received):
        """
        Prints to stdout a summery about packets integrity and round-trip time.
        :param time_delta_list:
        :param num_sent:
        :param num_received:
        :return: None.
        """
        print("\nPing statistics for {target_name}:{port}:".format(target_name=self.target_name, port=self.port))
        print("""   Packets: Sent = {num_sent}, Received = {num_received}, Lost = {num_lost} ({per_lost}% loss),
        """.format(num_sent=num_sent,
                   num_received=num_received,
                   num_lost=num_sent - num_received,
                   per_lost=((num_sent - num_received) / num_sent) * 100))
        if len(time_delta_list) > 0:
            print("Approximate round trip times in milli-seconds:")
            print("   Minimum = {min_time}ms, Maximum = {max_time}ms, Average = {avg_time}ms".format(
                  min_time=min(time_delta_list),
                  max_time=max(time_delta_list),
                  avg_time=sum(time_delta_list)/len(time_delta_list)))

    def ping(self):
        """
        Sends packets to the listening server according to the parameters chosen.
        :return: None
        """
        print("Pinging {target_name}:{port} with {size} bytes of data:".format(target_name=self.target_name,
                                                                               port=self.port,
                                                                               size=str(self.size)))
        start_time, end_time, send_data, received_data = None, None, b'', b''
        num_sent = 0
        num_received = 0
        round_trip_time_list = []

        try:

            # Set condition according to count / continuous flags.
            if self.continuous:
                condition = "True"
            else:
                condition = "i < self.count"

            i = 0
            while eval(condition):
                is_timeout = False
                if self.l4_protocol == "TCP":
                    try:
                        send_data = create_data_string(self.size)
                        start_time = datetime.datetime.now()
                        try:
                            # Set timeout and record round trip time.
                            self._socket.settimeout(self.timeout / 1000)  # socket.settimeout works in seconds.
                            self._socket.sendall(send_data)
                            received_data = self._socket.recv(self.response_buffer_size)
                            self._socket.settimeout(None)
                        except socket.timeout:
                            is_timeout = True
                        end_time = datetime.datetime.now()
                        num_sent += 1
                    except socket.error as e:
                        print(e)
                        exit(0)

                elif self.l4_protocol == "UDP":
                    try:
                        send_data = create_data_string(self.size)
                        start_time = datetime.datetime.now()
                        try:
                            # Set timeout and record round trip time.
                            self._socket.settimeout(self.timeout / 1000)  # socket.settimeout works in seconds.
                            self._socket.sendto(send_data, (self.target_name, self.port))
                            received_data, server = self._socket.recvfrom(self.response_buffer_size)
                            self._socket.settimeout(None)
                        except socket.timeout:
                            is_timeout = True
                        end_time = datetime.datetime.now()
                        num_sent += 1
                    except socket.error as e:
                        print(e)
                        exit(0)

                # Build current trip statistics and print it.
                if not is_timeout:
                    num_received = num_received + 1 if send_data == received_data else num_received
                    round_trip_time = self._millis_interval(start_time, end_time)
                    round_trip_time_list.append(round_trip_time)
                    round_trip_time = "=" + str(int(round_trip_time)) if round_trip_time >= 1.0 else "<1"

                    print("Reply from {target_name}{port}: bytes={num_bytes} time{num_milis}ms".format(
                          target_name=self.target_name,
                          port=self.port,
                          num_bytes=str(len(received_data)),
                          num_milis=round_trip_time))
                elif is_timeout:
                    print("Request timed out.")
                i += 1
        # Enable keyboard interrupt, mainly to allow a safe stop for the continuous mode.
        except KeyboardInterrupt:
            print("Keyboard Interrupted...")
        self._plot_ping_statistics(round_trip_time_list, num_sent, num_received)


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, add_help=False,
                                     description="Client side of a client-server ping emulation over transport layer.")
    parser.add_argument("-h", "--help", action="help", help="Show help message and exit")
    parser.add_argument("--version", action="version", version="1.0", help="Show program's version number and exit")
    parser.add_argument("-n", dest="count", help="Number of echo requests to send (Default: 4).", default=4, type=int)
    parser.add_argument("-t", dest="continuous", help="Ping the specified host until stopped.",
                        default=False, action='store_true')
    parser.add_argument("-s", dest="size", help="Send buffer size (Default:32).", default=32, type=int)
    parser.add_argument("-w", dest="timeout", help="Timeout in milliseconds to wait for each reply (Default: 4000 ms)",
                        default=4000, type=int)
    parser.add_argument("-l", dest="l4_protocol", help="Transport layer protocol, supports TCP/UDP (Default: TCP).",
                        default="TCP", type=str)
    parser.add_argument("-p", dest="port", help="Target's port (Default: 80).", default=80, type=int)
    parser.add_argument("-r", dest="response_buffer_size", help="Response buffer size (Default: 1024).",
                        default=1024, type=int)
    parser.add_argument("target_name", help="Target's IP address or host name.", type=str)
    args = parser.parse_args()
    return args


def main():

    # Parse CLI arguments into variables.
    conf = parse_args()
    count = conf.count
    continuous = conf.continuous
    size = conf.size
    timeout = conf.timeout
    l4_protocol = conf.l4_protocol
    port = conf.port
    target_name = conf.target_name
    response_buffer_size = conf.response_buffer_size

    # Initialize a client instance and send a ping request.
    ping_client = PingClient(target_name, count, continuous, size, timeout, l4_protocol, port, response_buffer_size)
    ping_client.ping()


if __name__ == '__main__':
    main()
