from threading import Thread

class LoopingThread(Thread):
    """This class performs update every loop
        on completion (if not canceled) it calls callback"""
    def __init__(self, stopEvent, cancelEvent, update, callback):
        super(LoopingThread, self).__init__()
        self.stopped = stopEvent
        self.canceled = cancelEvent
        self.update = update
        self.callback = callback

    def run(self):
        while not self.stopped.wait(1) and not self.canceled.wait(0):
            self.update()

        if not self.canceled.wait(0):
            self.callback()


