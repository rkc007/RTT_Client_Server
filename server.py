import argparse

import mysocket
import utils
import socket


parser = argparse.ArgumentParser(description="Launch server here.")
parser.add_argument(
    "type", metavar="TYPE", choices=["TCP"], help="Choose TCP for protocol.",
)
parser.add_argument("port", metavar="PORT", type=int, help="Set port to use.")

args = parser.parse_args()
print(socket.gethostname())

server = mysocket.serversocket(type=utils.type_map[args.type], port=args.port)
server.activate()
