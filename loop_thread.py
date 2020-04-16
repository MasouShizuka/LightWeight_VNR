from threading import Thread, Event

class Loop_Thread(Thread):
    def __init__(self, target=None, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.target = target
        self.__working = Event()
        self.__working.set()
        self.__flag = Event()
        self.__flag.set()

    def stop(self):
        self.__flag.set()
        self.__working.clear()

    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def run(self):
        while self.__working.isSet():
            self.__flag.wait()
            self.target(*self.args, **self.kwargs)