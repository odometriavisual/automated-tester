import io
import os
import time as time
from utils import generate_random_num


class SplitFrames(io.BufferedIOBase):
    def __init__(self, trigger, t0=0, root=""):
        self.t0 = t0
        self.frame_num = 1
        self.trigger = trigger
        self.output = None
        self.path = root + f'/picamera_#1111/'
        self.path = self.path[:-6] + f"#{generate_random_num(self.t0)}/"  # Generate a new folder name
        os.makedirs(self.path)

    def write(self, buf):
        self.trigger.wait()
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; close the old one (if any) and
            # open a new output

            if self.output:
                self.output.close()
            #Pega os valores dos sensores e o timestamp atual e salva como uma nova linha no txt
            timestamp = (time.time() - self.t0) * 1000  # in ms
            self.output = io.open(self.path + f'frame_#{self.frame_num:02d}_t{timestamp:.1f}.jpg', 'wb')
            self.frame_num += 1
        self.output.write(buf)
