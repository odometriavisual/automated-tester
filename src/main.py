from acquisition_system import AcquisitionSystem
from picamera import Picamera
from webcam import Webcam
from motor import Motor
import time
import multiprocessing

if __name__ == "__main__":
    root = "/home/pi/repos/automated-tester/data"
    fps = 30
    acquisitions = [
        [(6000, 6e3), (6000, 0)],  # Acquisition 1
        [(7000, 6e3), (7000, 0)],  # Acquisition 2
    ]

    acquisition_system = AcquisitionSystem(fps, root)

    motor = Motor()

    time.sleep(1)
    for acquisiton in acquisitions:
        acquisition_system.start()

        print("Acquisiton started")
        for command in acquisiton:
            time.sleep(1)  # Waits between movement

            speed, position = command
            motor.move(speed, position)
            motor.movement_done.wait()  # Waits for the movement end to start the next
            motor.movement_done.clear()  # Resets the event

        acquisition_system.stop()
        time.sleep(2)
    print(acquisition_system.acquisition_order)
