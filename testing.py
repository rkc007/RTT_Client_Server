import numpy
import socket

import mysocket
import stats
import utils


def roundtrip(msgsizes, type, host, port, delay, *args, **kwargs):
    type = utils.type_map[type]
    msgsizes = sorted(msgsizes)
    print(delay)

    labels = numpy.fromiter((2 ** msgsize for msgsize in msgsizes), numpy.float)
    data = numpy.array(
        [
            list(roundtrip_generator(msgsize, 20, type, host, port, delay))
            for msgsize in msgsizes
        ]
    )
    print("m")
    return data, labels


def roundtrip_generator(msgsize, iterations, type, host, port, delay):
    print("s rtt", msgsize, iterations, delay)
    sock = None
    tries = 4
    while iterations > 0:
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            RTT = sock.roundtrip(msgsize, iterations, delay)
            if RTT is not None:
                iterations -= 1
                yield RTT
            elif tries > 0:
                tries -= 1
            else:
                iterations -= 1
        finally:
            tries = 4
            if sock is not None:
                sock.close()


def throughput(msgsizes, type, host, port, delay, *args, **kwargs):
    type = utils.type_map[type]
    labels = numpy.fromiter((2 ** msgsize for msgsize in sorted(msgsizes)), numpy.float)

    data = numpy.array(
        [
            list(throughput_generator(msgsize, 20, type, host, port, delay))
            for msgsize in sorted(msgsizes)
        ]
    )
    print("m")
    return data, labels


def throughput_generator(msgsize, iterations, type, host, port, delay):
    print("s tput", msgsize, iterations, delay)
    sock = None
    while iterations > 0:
        try:
            sock = mysocket.clientsocket(type=type, host=host, port=port)
            throughput = sock.throughput(msgsize, iterations, delay)
            if throughput is not None:
                iterations -= 1
                yield throughput
        finally:
            if sock is not None:
                sock.close()
