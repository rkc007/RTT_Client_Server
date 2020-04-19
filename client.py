import argparse
from os.path import isdir

import plot
import testing

parser = argparse.ArgumentParser(description="Launch Client here.")
parser.add_argument("output", metavar="OUTPUT", help="Output directory")
parser.add_argument(
    "mode",
    metavar="MODE",
    choices=["rtt", "tput", "all"],
    help="Select between RTT or Throughput or Both.",
)
parser.add_argument(
    "type", metavar="TYPE", choices=["TCP"], help="Choose TCP for protocol.",
)
parser.add_argument("host", metavar="HOST", help="Set host to connect to.")
parser.add_argument("port", metavar="PORT", type=int, help="Set port to use.")
parser.add_argument(
    "--client", metavar="CLIENT", default="client", help="Name of your client.",
)
parser.add_argument(
    "delay",
    metavar="SERVER_DELAY",
    default=0,
    type=float,
    help="Select sever delay time in seconds.",
)

args = parser.parse_args()

if not isdir(args.output):
    parser.error("directory {} does not exist".format(args.output))

roundtrip_payload_size = range(0, 11, 1)
throughput_payload_size = range(10, 16, 1)


roundtrip_mode = lambda: plot.box_plot(
    *testing.roundtrip(roundtrip_payload_size, **args.__dict__),
    output=args.output,
    title="{} Round Trip Time from {} to {} with delay {}s".format(
        args.type, args.client, args.host, args.delay
    ),
    xlabel="Packet Size (B)",
    ylabel="RTT (s)",
)

throughput_mode = lambda: plot.box_plot(
    *testing.throughput(throughput_payload_size, **args.__dict__),
    output=args.output,
    title="{} Throughput from {} to {} with delay {}s".format(
        args.type, args.client, args.host, args.delay
    ),
    xlabel="Message Size (kB)",
    ylabel="throughput (kbps)",
    ymul=8 * 2 ** -10,
)


if args.mode in ["rtt", "all"]:
    roundtrip_mode()
if args.mode in ["tput", "all"]:
    throughput_mode()
