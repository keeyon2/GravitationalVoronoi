import random
import numpy as np
import colorsys
import sys
import time
import argparse

from qtreactor import pyqt4reactor
from PyQt4 import QtGui, QtCore

app = QtGui.QApplication(sys.argv)
pyqt4reactor.install()

from twisted.internet import reactor

import genVoronoi
from game_server import GameServerFactory

board_size = 1000

def hsv2rgb(h,s,v):
    return tuple(i * 255 for i in colorsys.hsv_to_rgb(h,s,v))

class MainWindow(QtGui.QWidget):

    def __init__(self, GUIOn, delay):
        self.GUIOn = GUIOn
        self.delay = delay
        super(MainWindow, self).__init__()
        self.colors = np.zeros([num_players, 3], dtype=np.uint8)
        self.dark_colors = np.zeros([num_players, 3], dtype=np.uint8)
        ci = 0
        for hue in xrange(0, 360, 360/num_players):
            light_color = np.array(
                [int(color) for color in hsv2rgb(hue/360.0, 0.75, 1)]
            )
            dark_color = np.array(
                [int(color) for color in hsv2rgb(hue/360.0, 0.75, 0.75)]
            )
            self.colors[ci] = light_color
            self.dark_colors[ci] = dark_color
            ci += 1
        genVoronoi.init_cache()
        self.points = np.zeros([num_players, num_moves, 2], dtype=np.int)
        self.points.fill(-1)
        self.player_names = []
        if self.GUIOn:
            self.image = QtGui.QImage(
                board_size/scale,
                board_size/scale,
                QtGui.QImage.Format_RGB888
            )
            ptr = self.image.bits()
            ptr.setsize(self.image.byteCount())
            self.imagenp = np.asarray(ptr).reshape(board_size/scale, board_size/scale, 3)
            self.initUI()
        else:
            # generate_voronoi_diagram needs this
            self.imagenp = np.zeros([board_size/scale, board_size/scale, 3], dtype=np.uint8)

    def addPlayerName(self, playerName):
        self.player_names.append(playerName)

    def initUI(self):
        self.imagenp[:,:] = np.array([255,255,255], dtype=np.uint8)

        pixmap = QtGui.QPixmap.fromImage(self.image)

        hbox = QtGui.QHBoxLayout(self)
        vbox = QtGui.QVBoxLayout(self)
        self.lbl = QtGui.QLabel(self)
        self.lbl.setPixmap(pixmap)

        self.textlbl = []
        for p in range(num_players):
            self.textlbl.append(QtGui.QLabel(self))

        okButton = QtGui.QPushButton("Reset")

        hbox.addWidget(self.lbl)

        for p in range(num_players):
            self.textlbl[p].setAutoFillBackground(True)
            self.textlbl[p].setFixedHeight(40)
            vbox.addWidget(self.textlbl[p])

        self.announcer = QtGui.QLabel(self)
        vbox.addWidget(self.announcer)
        vbox.addStretch(1)
        vbox.addWidget(okButton)
        hbox.addLayout(vbox)

        self.setLayout(hbox)

        self.setWindowTitle('Gravitational Voronoi B-)')

        okButton.mousePressEvent = self.resetUI

        self.show()

    def announce(self, player_scores):
        winner = max(player_scores.iteritems(), key=lambda p: p[1])[0]
        self.announcer.setText(winner + ' wins.')

    def resetNonUI(self):
        self.points.fill(-1)
        self.player_names = []

    def resetUI(self, event):
        self.resetNonUI()
        if self.GUIOn:
            self.imagenp[:,:] = np.array([255,255,255], dtype=np.uint8)
            pixmap = QtGui.QPixmap.fromImage(self.image)
            self.lbl.setPixmap(pixmap)
            self.announcer.setText('')
            for p in range(num_players):
                self.textlbl[p].setText('')

    def updateUI(self, player, move, move_num):
        if move_num == num_moves:
            return
        x_pos, y_pos = move

        self.points[player, move_num, 0] = x_pos
        self.points[player, move_num, 1] = y_pos

        t1 = time.time()
        genVoronoi.generate_voronoi_diagram(
            num_players,
            num_moves,
            self.points,
            self.colors,
            self.imagenp,
            self.GUIOn,
            scale
        )
        #print "Time to set pixels", time.time() - t1
        if self.GUIOn:
            t2 = time.time()
            pixmap = QtGui.QPixmap.fromImage(self.image)
            self.lbl.setPixmap(pixmap)

            painter = QtGui.QPainter()
            painter.begin(self.lbl.pixmap())
            for p in xrange(num_players):
                for m in xrange(num_moves):
                    if self.points[p, m, 0] == -1:
                        break
                    painter.setBrush(
                        QtGui.QColor(
                            self.dark_colors[p][0],
                            self.dark_colors[p][1],
                            self.dark_colors[p][2]
                        )
                    )
                    painter.drawEllipse(
                        (self.points[p, m, 0] - 2*scale)/scale,
                        (self.points[p, m, 1] - 2*scale)/scale,
                        4,
                        4,
                    )
            del painter
            #print "Time to draw ellipses", time.time() - t2

            scores = self.get_scores()
            for p in range(num_players):
                font = self.textlbl[p].font();
                if (player+1)%num_players == p:
                    font.setPointSize(24);
                    font.setBold(True);
                else:
                    font.setPointSize(18);
                self.textlbl[p].setFont(font);
                palette = self.textlbl[p].palette()
                role = self.textlbl[p].backgroundRole()
                color = QtGui.QColor(
                    self.colors[p][0],
                    self.colors[p][1],
                    self.colors[p][2]
                )
                palette.setColor(role, color)
                palette.setColor(self.textlbl[p].foregroundRole(), QtCore.Qt.white)
                self.textlbl[p].setPalette(palette)
                self.textlbl[p].setAlignment(QtCore.Qt.AlignCenter)
                self.textlbl[p].setText(self.player_names[p]+": "+str(scores[p]))
                self.textlbl[p].adjustSize()

        if self.delay - time.time() + t1 > 0:
            time.sleep(self.delay - time.time() + t1)

    def get_scores(self):
        scores_np = genVoronoi.get_scores(num_players)
        scores = [scores_np[p] for p in range(num_players)]
        return scores

    def closeEvent(self, event):
        print "Window closed."
        reactor.stop()
        event.accept()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_players", type=int, default=2,
                        help="Number of Players.")
    parser.add_argument("-f", "--first_player", default="abc",
                        help="Player who makes first move.")
    parser.add_argument("-m", "--num_moves", type=int, default=10,
                        help="Number of moves in the game.")
    parser.add_argument("-g", "--gui_on", type=int, choices=[0, 1], default=1,
                        help="If GUI is required.")
    parser.add_argument("-s", "--scale", type=int, choices=[1, 2], default=2,
                        help="Scale down the GUI size.")
    parser.add_argument("-d", "--delay", type=float, default=0,
                        help="Delay in seconds after each move. Accepts floats.")
    parser.add_argument("-e", "--experiments", type=int, default=0,
                        help="Number of experiments to run.")
    parser.add_argument("-p", "--port", type=int, default=1337,
                        help="Port number to run server on.")
    args = parser.parse_args()
    num_players = args.num_players
    start_player = args.first_player
    num_moves = args.num_moves
    gui_on = args.gui_on
    scale = args.scale
    delay = args.delay
    experiments = args.experiments
    port = args.port
    if experiments:
        experiments -= 1
        gui_on = 0
    mainWin = MainWindow(gui_on, delay)
    gsfactory = GameServerFactory(mainWin, start_player, num_players, num_moves, gui_on, experiments)
    reactor.listenTCP(port, gsfactory)
    reactor.runReturn()
    sys.exit(app.exec_())
