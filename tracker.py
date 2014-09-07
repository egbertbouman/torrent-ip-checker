import sys
import time
import signal
import struct
import socket
import select
import argparse


# Source bencode function: https://gist.github.com/pyropeter/642505
def bencode(obj):
    if isinstance(obj, int):
        return "i" + str(obj) + "e"

    if isinstance(obj, str):
        return str(len(obj)) + ":" + obj

    if isinstance(obj, list):
        res = "l"
        for elem in obj:
            res += bencode(elem)
        return res + "e"

    if isinstance(obj, dict):
        res = "d"
        for key in sorted(obj.keys()):
            res += bencode(key) + bencode(obj[key])
        return res + "e"

    raise Exception, "Unknown object: %s" % repr(obj)


class UDPTracker(object):

    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        self.socket.bind(('0.0.0.0', port))
        print 'UDP tracker: listening on port %d' % port

    def handle_request(self):
        request, addr = self.socket.recvfrom(1024)
        print "UDP tracker: received request", request.encode('hex')

        # Check request
        try:
            connection_id, action, transaction_id = struct.unpack_from('!QII', request)
        except:
            print "UDP tracker: ignoring request", request.encode('hex'), 'from %s:%d' % addr
        if action != 0:
            print "UDP tracker: client sent request with unsupported action", action
            return
        if connection_id != 0x41727101980:
            print "UDP tracker: client sent connection request with invalid connection_id ", connection_id
            return

        # Respond to connection request with an error message containing the client IP.
        response = struct.pack('!II', 3, transaction_id) + 'Your IP is %s:%d' % addr
        self.socket.sendto(response, addr)
        print "UDP tracker: sending response", response.encode('hex'), 'to %s:%d' % addr


class TCPTracker(object):

    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.socket.bind(('0.0.0.0', port))
        self.socket.listen(1)
        print 'TCP tracker: listening on port %d' % port

    def handle_request(self):
        conn, addr = self.socket.accept()
        request = conn.recv(1024)
        print "TCP tracker: received request", request.split('\n')[0]

        bencoded_dict = bencode({'failure reason': 'Your IP is %s:%d' % addr})
        headers = 'HTTP/1.1 200 OK\n'
        headers += 'Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + '\n'
        headers += 'Server: torrent-ip-checker\n'
        headers += 'Connection: close\n\n'
        response = headers + bencoded_dict
        conn.send(response)
        print "TCP tracker: sending response", response.split('\n')[0], 'to %s:%d' % addr
        conn.close()


def main(argv):
    parser = argparse.ArgumentParser(description='Runs a fake tracker that only reports back the ' +
                                                 'IP of the connecting client.')

    try:
        parser.add_argument('-u', '--udp', help='UDP port')
        parser.add_argument('-t', '--tcp', help='TCP port')
        parser.add_help = True
        args = parser.parse_args(sys.argv[1:])

    except argparse.ArgumentError:
        parser.print_help()
        sys.exit(2)

    udp_port = int(args.udp) if args.udp else None
    tcp_port = int(args.tcp) if args.tcp else None

    if udp_port == None and tcp_port == None:
        print 'You need to provide a TCP port, UDP port, or both.'
        sys.exit(1)

    signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0))
    print 'Press Ctrl+C to quit'

    trackers = {}
    if udp_port != None:
        t = UDPTracker(udp_port)
        trackers[t.socket] = t
    if tcp_port != None:
        t = TCPTracker(tcp_port)
        trackers[t.socket] = t

    while True:
        readable, _, _ = select.select(trackers.keys(), [], [])
        trackers[readable[0]].handle_request()


if __name__ == "__main__":
    main(sys.argv[1:])
