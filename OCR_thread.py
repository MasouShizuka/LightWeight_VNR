from threading import Thread, Event

class OCR_thread(Thread):
    def __init__(self, target=None, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.target = target
        self.__work = Event()
        self.__work.set()
        self.__flag = Event()
        self.__flag.set()

    def stop(self):
        self.__flag.clear()

    def pause(self):
        self.__work.clear()

    def resume(self):
        self.__work.set()

    def run(self):
        while self.__flag.isSet():
            self.__work.wait()
            self.target(*self.args, **self.kwargs)