from picamera2 import Picamera2
from picamera2.outputs import FileOutput
from picamera2.encoders import JpegEncoder
from splitframes import SplitFrames
from utils import generate_random_num
import time

class Picamera():
    def __init__(self, t0, root, fps=60):
        self.root = root
        self.t0 = t0
        self.fps = fps
    
    def record(self, start, stop):
        camera = Picamera2()
        camera.start_preview()
        config = camera.create_preview_configuration(main = {"size" : (640, 480)})
        camera.configure(config)
        
        ctrls = {
            "ExposureTime": 20  ,
            'FrameDurationLimits' : (int(1/self.fps * 1e6), 100000)
        }
        camera.set_controls(ctrls)
        print("Picamera setup done.")
        
        try:
            encoder = JpegEncoder(q=70)
            output = SplitFrames(start, self.t0, self.root)
            print("Picamera started recording")
            camera.start_recording(encoder, FileOutput(output))
        finally:
            stop.wait()
            camera.stop_recording()
            print("Picamera stopped recording")