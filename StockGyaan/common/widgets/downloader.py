import time

from PyQt5.QtCore import pyqtSignal, QThread

from common.utils_ import err, setUpParent, dbgOK


class Downloader(QThread):

    downloaded = pyqtSignal()

    def __init__(self, parent=None):
        super(QThread, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        if not hasattr(self.parent, "task_queue"):
            err(self, "Error, no task queue")
        if not hasattr(self.parent, "periodic_queue"):
            err(self, "Error, no periodic queue")

    def run(self):
        i = 0
        while self.parent.run_threads:
            if not self.parent.task_queue:
                dbgOK(self, "No tasks")
            else:
                obj = self.parent.task_queue.pop()
                obj.download()
                self.downloaded.emit()

            if i == 0:
                dbgOK(self, " periodic update ... ")
                if not self.parent.periodic_queue:
                    dbgOK(self, "No periodic")
                else:
                    for obj in self.parent.periodic_queue:
                        obj.download()
                    self.downloaded.emit()
            i = (i + 2) % self.parent.thread_update_interval
            time.sleep(2)
