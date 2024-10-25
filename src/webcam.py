import os
import cv2
import time
import json
from utils import generate_random_num

class Webcam():
    def __init__(self, t0, root, fps=60, sync_save=False):
        self.t0 = t0
        self.fps = fps
        self.frame_num = 1
        self.camera_id = 0
        self.setup(self.camera_id)
        self.path = root + f"/webcam_#1111/"
        self.prev_frame_time = 0 # Variables Used to Calculate FPS
        self.new_frame_time = 0
        self.sync_save = sync_save
        self.id = 0
        
    def setup(self, camera_id):
        self.configs = {
            "TYPE": "SUBSEA IMX719",
            "WIDTH": 1280,
            "HEIGHT": 720,
            "FPS": 120,
            "EXPOSURE": 50,
            "EXPOSURE MODE": 1 # Manual         
        }
        
        self.vid = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.configs["WIDTH"])
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.configs["HEIGHT"])
        self.vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.vid.set(cv2.CAP_PROP_FPS, self.configs["FPS"]) # Its necessary in order to use the 60 FPS cap of C922 at 720p set 120 FPS
        self.vid.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.configs["EXPOSURE MODE"]) # manual mode
        self.vid.set(cv2.CAP_PROP_EXPOSURE, self.configs["EXPOSURE"]) # This should return a black frame  
        print("Webcam setup done.")
    
    def record(self, start, stop):
        self.id = generate_random_num(self.t0)
        self.path = self.path[:-6] + f"#{self.id}/" # Generate a new folder name
        os.makedirs(self.path)
        
        # 
        with open(self.path + 'configs.json', 'w', encoding='utf-8') as file:
            json.dump(self.configs, file, ensure_ascii=False, indent=4)
          
        
        if not self.sync_save:
            frames = list()
            timestamps = list() 
        try:
            _, frame = self.vid.read() # Starts the communication
            print("Webcam ready to record.")    
            start.wait()
            print("Webcam started recording.")     
            while not stop.is_set():      
                before = time.time()
                flag, frame = self.vid.read()
                timestamp = (time.time() - self.t0) * 1000 # in ms
                if self.sync_save:
                    cv2.imwrite(self.path + f'frame_#{self.frame_num:02d}_t{timestamp:.1f}.jpg', frame)
                else:
                    frames.append(frame)
                    timestamps.append(timestamp)
                self.frame_num += 1
                #print(f"FPS ≃ {1/(time.time() - before)}")
        finally:
            time.sleep(.5)
            self.vid.release()
            print("Webcam stopped recording.")
            if not self.sync_save:
                save_frames(self.path, timestamps, frames)
        
        
def save_frames(path, timestamps, frames):
    i = 0
    for timestamp, frame in zip(timestamps, frames):
        cv2.imwrite(path + f'frame_#{(i + 1):02d}_t{timestamp:.1f}.jpg', frame)
        i += 1
    

