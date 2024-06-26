import os
from datetime import datetime

class Logger:
    DIR_NAME = 'logs'
    LOG_EXTENSION = '.log'
    LOG_FILENAME = 'info'
    today = None

    def __init__(self):
        self.today = datetime.today().strftime("%d.%m.%Y")
        self.check_dir()

    def check_dir(self):
        if not os.path.exists(os.path.join(self.DIR_NAME)):
            os.mkdir(os.path.join(self.DIR_NAME))
        if os.path.exists(os.path.join(self.DIR_NAME, self.today)):
            return
        os.mkdir(os.path.join(self.DIR_NAME, self.today))
        return

    def check_file(self):
        f = open(os.path.join(self.DIR_NAME, self.today, self.LOG_FILENAME + self.LOG_EXTENSION), 'w')
        f.close()

    def add(self, data: str):
        #self.check_file()
        with open(os.path.join(self.DIR_NAME, self.today, self.LOG_FILENAME + self.LOG_EXTENSION), "a") as f:
            f.write(data)
            f.write('\n')
            f.write('==========')
            f.write('\n')
        return
