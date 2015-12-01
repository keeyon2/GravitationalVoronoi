import sys
import random
import time
import argparse
import math

from twisted.internet import reactor, protocol

board_size = 1000
board_matrix = [[0 for x in range(1000)] for x in range(1000)]

class Client(protocol.Protocol):
    """Random Client"""
    def __init__(self, name):
        self.name = name
        self.prev_moves = []
        self.my_moves = []
        self.their_moves = []

    def reset(self):
        print "Reset called"
        self.prev_moves = []
        self.my_moves = []
        self.their_moves = []

    def make_random_move(self):
        move = None
        while not move:
            x = random.randint(0, board_size-1)
            y = random.randint(0, board_size-1)
            if (x, y) not in self.prev_moves:
                move = (x, y)
        return move

    def find_closest_move_to_point(self, point, player_id):
        min_distance = sys.maxint
        min_move = (-100, -100)

        if player_id == 1:
            moves = self.my_moves
        else:
            moves = self.their_moves

        for move in moves:
            distance = self.compute_euc_distance(point, move)
            if distance < min_distance:
                min_distance = distance
                min_move = move
        
        return move

    def find_pull_for_point(self, point, player_id):
        distances = []
        if player_id == 1:
            for move in self.my_moves:
               distances.append(self.compute_euc_distance(move, point))

        else:
            for move in self.their_moves:
                distances.append(self.compute_euc_distance(move, point))

        pull = 0
        for distance in distances:
            if distance == 0:
                return sys.maxint

            pull = pull + (1 / (distance * distance))

        return pull

    def compute_euc_distance(self, point1, point2):
        x_distance = point1[0] - point2[0]
        x_distance = math.pow(x_distance, 2)
        y_distance = point1[1] - point2[1]
        y_distance = math.pow(y_distance, 2)

        return math.sqrt(x_distance + y_distance)

    def update_board_with_move(self, move, personId):
        if personId == 1:
            self.my_moves.append(move)
            board_matrix[move[0]][move[1]] = 1
        else:
            self.their_moves.append(move)
            board_matrix[move[0]][move[1]] = 2

        self.prev_moves.append(move);

    def decide_my_move(self):
        if not self.prev_moves:
            return (499, 499)
        else:
            #return self.make_random_move()
            their_min_point_pull = sys.maxint
            min_pull_location = (-100, -100) 
            for y in range(1000):
                for x in range(1000):
                    my_pull = self.find_pull_for_point( (x, y), 1)
                    their_pull = self.find_pull_for_point( (x, y), 2)

                    if their_pull > my_pull:
                        if their_pull < their_min_point_pull:
                            their_min_point_pull = their_pull
                            min_pull_location = (x, y)

            their_closest_point = self.find_closest_move_to_point(min_pull_location, 2)

            move_x_right = their_closest_point[0] < min_pull_location[0]
            move_y_down = their_closest_point[1] < min_pull_location[1]

            my_move = None
            amount = 1
            while not my_move: 
                if move_x_right:
                    move_x = their_closest_point[0] + amount
                    if move_x > 999:
                        move_x = 999
                else:
                    move_x = their_closest_point[0] - amount
                    if move_x < 0:
                        move_x = 0

                if move_y_down:
                    move_y = their_closest_point[1] + amount
                    if move_y > 999:
                        move_y = 999

                else:
                    move_y = their_closest_point[1] - amount
                    if move_y < 0:
                        move_y = 0

                if (move_x, move_y) not in self.prev_moves:
                    my_move = (move_x, move_y)
                    return my_move

                else:
                    if (move_x == 0 or move_x == 999):
                        if (move_y == 0 or move_y == 999):
                            print "HAD TO RETURN RANDOM, SHOULD NEVER HAPPEN"
                            return self.make_random_move()

                    amount = amount + 1

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
                # self.prev_moves.append((x, y))
                # self.their_moves.append((x, y))
                self.update_board_with_move((x, y), 2)
                print "We have received move x: %d and y: %d" % (x, y)
            #This is the first move
            #move = self.make_random_move()
            move = self.decide_my_move()
            self.update_board_with_move(move, 1)
            print "making move %r" % str(move)
            self.transport.write("{0} {1}".format(move[0], move[1]))
        elif items[-1] == "END":
            for i in self.prev_moves:
                print ("Prev move x and y: %r %r" % (str(i[0]), str(i[1])))
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
