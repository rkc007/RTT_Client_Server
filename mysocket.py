import socket
import time

import utils

# Predefined Socket library bytes for sending messages
ACK, NACK, MODE_ROUNDTRIP, MODE_THROUGHPUT, VAL = range(25, 100, 15)
ACK = bytes([ACK])
NACK = bytes([NACK])


class mysocket(socket.socket):
    """A subclass of socket adding methods for TCP testing."""

    def __init__(self, port=8888, udp_timeout=1.0, *args, **kwargs):
        super(mysocket, self).__init__(*args, **kwargs)
        self.port = port

    def sendby(self, msg, msgsize, bufsize):
        """Sends an entire message in chunks of size bufsize"""
        if msgsize < bufsize:
            bufsize = msgsize
        sent = 0

        start_time = time.time()

        while sent < msgsize:
            sent += self.send(msg[sent : sent + bufsize])

        return start_time

    def recvby(self, msgsize, bufsize):
        """Receives an entire message in chunks of size bufsize"""
        received = 0
        msg = b""
        timed_out = False

        try:
            while received < msgsize:
                buffer = self.recv(bufsize)
                received += len(buffer)
                msg += buffer
        # print("received: {}".format(received))
        except socket.timeout:
            timed_out = True
        finally:
            return msg, received, timed_out

    def is_tcp(self):
        """Return whether or not the socket is using TCP"""
        return utils.get_bit(self.type, socket.SOCK_STREAM - 1)


class serversocket(mysocket):
    """A subclass of mysocket for server-side network performance testing"""

    def __init__(self, *args, **kwargs):
        super(serversocket, self).__init__(*args, **kwargs)
        self.host = socket.gethostname()

    def accept(self):
        """accept() -> (socket object, address info)
        Wait for an incoming connection.  
        """
        fd, addr = self._accept()
        sock = serversocket(
            family=self.family, type=self.type, proto=self.proto, fileno=fd
        )

        if socket.getdefaulttimeout() is None and self.gettimeout():
            sock.setblocking(True)
        return sock, addr

    def activate(self, *args, **kwargs):
        self.bind((self.host, self.port))
        if self.is_tcp():
            print("Waiting for Client Connection")
            return self._tcp_loop(*args, **kwargs)
        else:
            raise ValueError("type {} serversocket not implemented".format(self.type))

    def _tcp_loop(self, *args, **kwargs):
        count = 0
        """Listen for client connections over TCP and react accordingly."""
        try:
            self.listen(1)

            while True:
                client, address = self.accept()
                print("connected to {}".format(address))

                try:
                    if count < 1:
                        print("200 OK: Ready")
                        count = count + 1
                    # receive 2-byte command message from client.
                    # first byte selects the mode, the other is a mode-specific
                    # option to be interpreted by that mode's function, here it is TCP
                    commands = client.recv(2)
                    mode, option = commands

                    if mode == MODE_ROUNDTRIP:
                        self._roundtrip_tcp(client, option, *args, **kwargs)
                    elif mode == MODE_THROUGHPUT:
                        self._throughput_tcp(client, option, *args, **kwargs)
                    else:
                        client.send(NACK)
                        print("mode {} not implemented".format(mode))
                finally:
                    client.close()
        finally:
            self.close()

    def _roundtrip_tcp(self, client, msgsize, *args, **kwargs):
        """Perform roundtrip performance measurements using TCP,
        server-side."""
        msgsize = 2 ** msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)[0]
        # send message back
        client.sendby(msg, msgsize, msgsize)

    def _throughput_tcp(self, client, msgsize, *args, **kwargs):
        """Perform throughput performance measurements using TCP,
        server-side."""
        msgsize = 2 ** msgsize
        client.send(ACK)

        # receive message
        msg = client.recvby(msgsize, msgsize)[0]
        # echo message
        client.sendall(msg)


class clientsocket(mysocket):
    """A subclass of mysocket for client-side network performance testing"""

    def __init__(self, host="", *args, **kwargs):
        super(clientsocket, self).__init__(*args, **kwargs)
        self.host = host
        if self.is_tcp():
            self.connect((self.host, self.port))

    def roundtrip(self, msgsize, iterations, delay, *args, **kwargs):
        """Perform roundtrip performance measurements, client-side."""
        if self.is_tcp():
            return self._roundtrip_tcp(msgsize, iterations, delay, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def throughput(self, msgsize, iterations, delay, *args, **kwargs):
        """Perform throughput performance measurements, client-side."""
        if self.is_tcp():
            return self._throughput_tcp(msgsize, iterations, delay, *args, **kwargs)
        else:
            raise ValueError("type {} not supported".format(self.type))

    def _roundtrip_tcp(self, msgsize, iterations, delay, *args, **kwargs):
        """Perform roundtrip performance measurements using TCP,
        client-side."""
        self.sendall(bytes([MODE_ROUNDTRIP, msgsize]))
        if self.recv(1) is NACK:
            return

        msgsize = 2 ** msgsize
        msg = utils.makebytes(msgsize)

        start_time = time.time()

        self.sendall(msg)
        recvmsg = self.recvby(msgsize, msgsize)[0]
        time.sleep(delay)
        print("m", recvmsg, iterations)

        end_time = time.time()
        elapsed_time = end_time - start_time

        return elapsed_time

    def _throughput_tcp(self, msgsize, iterations, delay, *args, **kwargs):
        """Perform throughput performance measurements using TCP,
        client-side."""
        self.sendall(bytes([MODE_THROUGHPUT, msgsize]))
        if self.recv(1) is NACK:
            return

        msgsize = 2 ** msgsize
        msg = utils.makebytes(msgsize)

        start_time = time.time()

        self.sendall(msg)
        recvmsg = self.recvby(msgsize, msgsize)
        time.sleep(delay)
        print("m", recvmsg, iterations)

        end_time = time.time()
        elapsed_time = end_time - start_time

        return 2 * msgsize / elapsed_time
