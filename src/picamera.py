from picamera2 import Picamera2
from picamera2.outputs import FileOutput
from picamera2.encoders import JpegEncoder
from splitframes import SplitFrames
from utils import generate_random_num, calculate_teng_score
import time
from libcamera import controls
import numpy as np
import cv2


class Picamera:
    def __init__(self, t0, root, fps=60):
        self.root = root
        self.t0 = t0
        self.fps = fps
        self.camera = self.setup()

    def setup(self):
        camera = Picamera2()
        camera.start_preview()
        config = camera.create_preview_configuration(main={"size": (640, 480)})
        camera.configure(config)

        ctrls = {
            "ExposureTime": 20,
            'FrameDurationLimits': (int(1 / self.fps * 1e6), 100000)
        }
        camera.set_controls(ctrls)
        print("Picamera setup done.")
        return camera

    def record(self, start, stop):
        try:
            encoder = JpegEncoder(q=70)
            output = SplitFrames(start, self.t0, self.root)
            print("Picamera started recording")
            self.camera.start_recording(encoder, FileOutput(output))
        finally:
            stop.wait()
            self.camera.stop_recording()
            print("Picamera stopped recording")

    def take_picture(self):
        capture_config = self.camera.create_still_configuration()
        image_rgb = self.camera.switch_mode_and_capture_image(capture_config)
        frame = image_rgb
        return frame

    def set_focus(self, focus: float):
        # Ajusta o foco da câmera
        self.camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": float(focus)})

    def calibrate(self, calibration_start: int = 0, calibration_end: int = 15, calibration_step: int = 1):
        best_focus_value = None
        best_score = -float('inf')
        actual_focus = calibration_start

        self.set_focus(actual_focus)
        time.sleep(1)

        while actual_focus < calibration_end:
            actual_focus += calibration_step
            self.set_focus(actual_focus)
            time.sleep(0.3)

            frame = self.take_picture()
            score = calculate_teng_score(frame)

            if score > best_score:
                best_focus_value = actual_focus
                best_score = score
            print(f"Actual score = {actual_focus:5.2f}; \t Score = {score:5.2f} \n")

        else:
            self.set_focus(best_focus_value)
            time.sleep(0.5)
