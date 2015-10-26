import sys
import random
import time
import argparse

from twisted.internet import reactor, protocol

board_size = 1000

class Client(protocol.Protocol):
    """Random Client"""
    def __init__(self, name):
        self.name = name
        self.prev_moves = []

    def reset(self):
        print "Reset called"
        self.prev_moves = []

    def make_random_move(self):
        move = None
        while not move:
            x = random.randint(0, board_size-1)
            y = random.randint(0, board_size-1)
            if (x, y) not in self.prev_moves:
                move = (x, y)
        return move

    def dataReceived(self, data):
        print "Received: %r" % data
        line = data.strip()
        items = line.split("\n")
        if items[-1] == "TEAM":
            self.transport.write(self.name)
        elif items[-1] == "MOVE":
            if items[0] == "RESTART":
                self.reset()
                del items[0]
            for item in items[:-1]:
                parts = item.split()
                # think for a random time 1-5 seconds, for testing only
                # time.sleep(random.randint(1, 5))
                player, x, y = parts[0], int(parts[1]), int(parts[2])
                # make a random move
                self.prev_moves.append((x, y))
            move = self.make_random_move()
            print "making move %r" % str(move)
            self.transport.write("{0} {1}".format(move[0], move[1]))
        elif items[-1] == "END":
            self.transport.loseConnection()
        elif items[-1] == "RESTART":
            self.reset()

    def connectionLost(self, reason):
        reactor.stop()

class ClientFactory(protocol.ClientFactory):
    """ClientFactory"""
    def __init__(self, name):
        self.name = name

    def buildProtocol(self, addr):
        c = Client(self.name)
        c.addr = addr
        return c

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Your name")
    parser.add_argument("-p", "--port", type=int, default="1337", help="Server port to connect to.")
    args = parser.parse_args()
    client_name = args.name
    port = args.port
    factory = ClientFactory(client_name)
    reactor.connectTCP("127.0.0.1", port, factory)
    reactor.run()


if __name__ == '__main__':
    main()
