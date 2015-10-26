import random
import numpy as np
import genVoronoi
import colorsys
import time
import argparse

import sys
from PyQt4 import QtGui, QtCore

num_players = 2
num_moves = 10
board_size = 1000
scale = 1

def hsv2rgb(h,s,v):
    return tuple(i * 255 for i in colorsys.hsv_to_rgb(h,s,v))

class MainWindow(QtGui.QWidget):

    def __init__(self):
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
        self.image = QtGui.QImage(
            board_size/scale,
            board_size/scale,
            QtGui.QImage.Format_RGB888
        )
        ptr = self.image.bits()
        ptr.setsize(self.image.byteCount())
        self.imagenp = np.asarray(ptr).reshape(board_size/scale, board_size/scale, 3)
        self.current_player = 0
        self.move = 0
        self.initUI()

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

        vbox.addStretch(1)
        vbox.addWidget(okButton)
        hbox.addLayout(vbox)

        self.setLayout(hbox)

        self.setWindowTitle('Gravitational Voronoi B-)')
        self.lbl.mousePressEvent = self.updateMouse
        okButton.mousePressEvent = self.resetUI

        self.show()

    def resetUI(self, event):
        self.current_player = 0
        self.move = 0
        self.points.fill(-1)
        self.imagenp[:,:] = np.array([255,255,255], dtype=np.uint8)
        pixmap = QtGui.QPixmap.fromImage(self.image)
        self.lbl.setPixmap(pixmap)

    def updateMouse(self, event):
        self.updateUI((event.pos().x(), event.pos().y()))

    def updateUI(self, move):
        if self.move == num_moves:
            return
        x_pos, y_pos = move

        self.points[self.current_player, self.move, 0] = x_pos
        self.points[self.current_player, self.move, 1] = y_pos

        t1 = time.time()
        genVoronoi.generate_voronoi_diagram(
            num_players,
            num_moves,
            self.points,
            self.colors,
            self.imagenp,
            1,
            scale
        )
        print "Time to set pixels", time.time() - t1

        t2 = time.time()
        pixmap = QtGui.QPixmap.fromImage(self.image)
        self.lbl.setPixmap(pixmap)
        print self.points
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
                    (self.points[p, m, 0] - 4*scale)/scale,
                    (self.points[p, m, 1] - 4*scale)/scale,
                    4*scale,
                    4*scale,
                )
        del painter
        print "Time to draw ellipses", time.time() - t2

        scores = self.get_scores()
        for p in range(num_players):
            font = self.textlbl[p].font();
            if (self.current_player+1)%num_players == p:
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
            self.textlbl[p].setText("Player "+str(p+1)+": "+str(scores[p]))
            self.textlbl[p].adjustSize()

        if self.current_player == num_players-1:
            self.move += 1
        self.current_player = (self.current_player + 1) % num_players
        if self.move == num_moves:
            print self.get_scores()

    def get_scores(self):
        scores_np = genVoronoi.get_scores(num_players)
        scores = [scores_np[p] for p in range(num_players)]
        return scores

    def closeEvent(self, event):
        print "Window closed."
        event.accept()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_players", type=int, default=2,
                        help="Number of Players.")
    parser.add_argument("-m", "--num_moves", type=int, default=10,
                        help="Number of moves in the game.")
    args = parser.parse_args()
    global num_players
    num_players = args.num_players
    global num_moves
    num_moves = args.num_moves
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
