"""
Author: Assaf Bentabou
Data: 24/02/20

Client-server python script for "ping" over TCP or UDP.
"""

import socket
import select
import argparse


class PingServer:
    def __init__(self,
                 port,
                 response_buffer_size,
                 hostname):
        self.hostname = hostname
        self.port = port
        self.response_buffer_size = response_buffer_size
        self.tcp_socket = None
        self.udp_socket = None
        self._init_tcp_socket()
        self._init_udp_socket()

    def __exit__(self):
        self.tcp_socket.close()
        self.udp_socket.close()

    def _init_tcp_socket(self):
        """
        Initializes a new TCP socket into 'self.tcp_socket'.
        :return: None
        """
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.bind((self.hostname, self.port))
            self.tcp_socket.listen()
        except socket.error as e:
            print(e)

    def _init_udp_socket(self):
        """
        Initializes a new UDP socket into 'self.udp_socket'.
        :return: None.
        """
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind((self.hostname, self.port))
        except socket.error as e:
            print(e)

    def _serve_tcp(self):
        """
        Echo received packets for the TCP socket.
        :return: None
        """
        try:
            conn, addr = self.tcp_socket.accept()
            print("Connected by " + str(addr) + " over TCP.")
            with conn:
                while True:
                    data = conn.recv(self.response_buffer_size)
                    if not data:
                        print('TCP client disconnected.')
                        break
                    else:
                        print("Recv TCP:'%s'" % data)
                        conn.sendall(data)
                conn.close()
        except ConnectionResetError as e:
            print("Client reset connection.")

    def _serve_udp(self):
        """
        Echo received packets for the UDP socket.
        :return: None
        """
        try:
            data, addr = self.udp_socket.recvfrom(self.response_buffer_size)
            print("Recv UDP:'%s'" % data)
            self.udp_socket.sendto(data, addr)
        except ConnectionResetError as e:
            print("Client reset connection.")

    def start(self):
        """
        Start the server up and listen to both TCP and UDP requests.
        Mange sockets idle times using 'select' lib.
        :return: None
        """
        listed_sockets = [self.tcp_socket, self.udp_socket]
        while True:
            read_ready, write_ready, exception_ready = select.select(listed_sockets, [], [])
            for sock in read_ready:
                if sock == self.tcp_socket:
                    self._serve_tcp()
                elif sock == self.udp_socket:
                    self._serve_udp()


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, add_help=False,
                                     description="Server side of a client-server ping emulation over transport layer.")
    parser.add_argument("-h", "--help", action="help", help="Show help message and exit")
    parser.add_argument("--version", action="version", version="1.0", help="Show program's version number and exit")
    parser.add_argument("-p", dest="port", help="Target's port (Default: 80).", default=80, type=int)
    parser.add_argument("-r", dest="response_buffer_size", help="Response buffer size (Default: 1024).",
                        default=1024, type=int)
    parser.add_argument("hostname", help="Hosts's IP address or host name.", type=str)
    args = parser.parse_args()
    return args


def main():

    # Parse CLI arguments into variables.
    conf = parse_args()
    port = conf.port
    response_buffer_size = conf.response_buffer_size
    hostname = conf.hostname

    # Initialize a server instance and listen for ping requests.
    ping_server = PingServer(port, response_buffer_size, hostname)
    ping_server.start()


if __name__ == '__main__':
    main()
