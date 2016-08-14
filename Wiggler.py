import sys
from os import path

from PyQt4 import uic
from PyQt4.Qt import *

from threading import Event
from LoopingThread import LoopingThread


main_ui     = uic.loadUiType(path.join('ui', 'app.ui'))[0]
count_ui    = uic.loadUiType(path.join('ui', 'count.ui'))[0]

class MainWindowClass(QMainWindow, main_ui):
    def __init__(self, parent=None):
        super(MainWindowClass, self).__init__()
        self.setupUi(self)
        self.btn_Start.clicked.connect(self.btn_Start_Clicked)
        self.btn_Wiggle.clicked.connect(wiggle)

    def btn_Start_Clicked(self):
        try:
            minutes = int(self.ipt_Minutes.text()) if self.ipt_Minutes.text() else 0
            seconds = int(self.ipt_Seconds.text()) if self.ipt_Seconds.text() else 0
            time    = minutes * 60 + seconds
            self.startTimer(time, wiggle)
        except ValueError as e:
            print(e)
            self.errorMessage('Please enter a number')
            self.ipt_Minutes.setText('')
            self.ipt_Seconds.setText('')

    def startTimer(self, time, fun):
        # Return if countdown = 0
        if time == 0:
            fun()
            return

        # Disable inputs
        self.ipt_Minutes.setEnabled(False)
        self.ipt_Seconds.setEnabled(False)
        self.chk_Repeat.setEnabled(False)

        # Open timer window
        self.window = TimerWindowClass(
            time, fun,#                     - Timer and function to perform
            self.timerWindowClosed,#        - Called when window closed or canceled
            self.chk_Repeat.checkState())#  - Repeat boolean
        self.window.show()

    def timerWindowClosed(self):
        # Enable inputs
        self.ipt_Minutes.setEnabled(True)
        self.ipt_Seconds.setEnabled(True)
        self.chk_Repeat.setEnabled(True)

    def errorMessage(self, message):
        QMessageBox.warning(
            self,
            'Warning',
            message,
            QMessageBox.Ok)


class TimerWindowClass(QWidget, count_ui):
    def __init__(self, time, func, close, repeat):
        super(TimerWindowClass, self).__init__()
        self.setupUi(self)
        self.btn_Cancel.clicked.connect(self.cancelTimer)
        self.lbl_Countdown.setText(renderTime(time))

        # Store variables
        self.time   = time
        self.clock  = time
        self.func   = func
        self.close  = close
        self.repeat = repeat

        # Stop and cancel flags
        self.stopFlag   = Event()
        self.cancelFlag = Event()

        # Start new Timer thread
        self.thread = LoopingThread(
            self.stopFlag,
            self.cancelFlag,
            self.updateClock,
            self.timerFinished)

        self.startTimer()

    def startTimer(self):
        self.thread.start()

    def cancelTimer(self):
        self.close()
        self.deleteLater()
        self.cancelFlag.set()

    def timerFinished(self):
        self.func()

        if self.repeat:
            self.clock = self.time
            self.stopFlag.clear()
            self.thread.run()
        else:
            self.deleteLater()
            self.close()

    def updateClock(self):
        self.lbl_Countdown.setText(renderTime(self.clock))
        if self.clock < 1:
            self.stopFlag.set()

        self.clock -= 1

def renderTime(t):
    from math import floor
    m = floor(t / 60)
    s = t % 60
    return '{}:{}'.format(int(m), s if s > 9 else '0' + str(s))

def wiggle():
    from pyautogui import moveRel
    moveRel( 10, None)
    moveRel(-20, None)
    moveRel( 10, None)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MainWindowClass(None)
    myWindow.show()
    ret = app.exec_()
    sys.exit(ret)
