import time
import multiprocessing
from picamera import Picamera
from webcam import Webcam


#
# acquisition  = [command 1, ..., command N]
# command 1 = (speed 1, position 1)
# 
# sequence = [acquisition 1, acquisition 2, ..., acquistion N]

class AcquisitionSystem:
    def __init__(self, fps=60, root=""):
        self.fps = fps
        self.root = root
        self.start_trigger = multiprocessing.Event()
        self.stop_trigger = multiprocessing.Event()
        self.acquisition_order = list()

    def start(self):
        self.t0 = time.time()
        self.picamera = Picamera(self.t0, self.root, self.fps)
        self.webcam = Webcam(self.t0, self.root, self.fps)

        # Resets the new acquisiton:
        self.p1 = multiprocessing.Process(target=self.picamera.record, args=(self.start_trigger, self.stop_trigger,))
        self.p2 = multiprocessing.Process(target=self.webcam.record, args=(self.start_trigger, self.stop_trigger,))
        time.sleep(2)

        # Starts the processes:
        self.p1.start()
        self.p2.start()
        time.sleep(2)
        self.start_trigger.set()

    def stop(self):
        self.stop_trigger.set()

        # Reset the 
        time.sleep(1)
        self.start_trigger.clear()
        self.stop_trigger.clear()
        self.p1.join()
        self.p2.join()
        self.acquisition_order.append(self.webcam.id)  # The name of the last acquisiton path
