import numpy as np
import multiprocessing
import RPi.GPIO as GPIO
import time

STEP_PIN = 3
DIR_PIN = 5


class Motor:
    def __init__(self, rampup_proportion=.1, rampdown_proportion=.1, max_position=13000, min_position=0,
                 curr_position=0):
        #
        if (rampup_proportion > 1 or rampup_proportion < 0) or (rampdown_proportion > 1 or rampdown_proportion < 0):
            raise ValueError("The soft-starter ramp-up and ramp-down proportion must be between 0 and 1.")
        else:
            self.rampup_proportion = rampup_proportion
            self.rampdown_proportion = rampdown_proportion

        # 
        if max_position < min_position:
            raise ValueError("Maximum position must be greater than minimum position.")
        else:
            self.max_position = max_position
            self.min_position = min_position
            self.movement_span = self.max_position - self.min_position

        # The current position always starts as zero:
        self.curr_position = curr_position

        # An event that signals that a movement has stopped:
        self.movement_done = multiprocessing.Event()
        self.movement_done.clear()

    def move(self, speed, desired_position):
        print(f"Current position: {self.curr_position}")
        print(f"Desired position: {desired_position}")
        if (self.curr_position + desired_position) > self.max_position or (
                self.curr_position + desired_position) < self.min_position:
            raise ValueError("Invalid position value.")
        else:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(STEP_PIN, GPIO.OUT)
            GPIO.setup(DIR_PIN, GPIO.OUT)

            try:
                # Moves:
                self.__move(speed, desired_position)

                # Signal that the movement is done:
                self.movement_done.set()
            finally:
                GPIO.output(STEP_PIN, False)
                GPIO.output(DIR_PIN, False)
                GPIO.cleanup()  # Limpa configuração

    def __move(self, desired_speed, desired_position):
        is_moving = True
        step_direction = 1 if desired_position > self.curr_position else -1
        print(step_direction)
        if step_direction == 1:
            GPIO.output(DIR_PIN, True)  # Sentido anti-horário
        else:
            GPIO.output(DIR_PIN, False)  # Sentido horário

        desired_position = desired_position
        total_steps = abs(desired_position - self.curr_position)
        steps_to_go = total_steps
        step_interval = 1 / desired_speed
        last_step_time = time.time()
        initial_slow_steps = total_steps * self.rampup_proportion
        final_slow_steps = total_steps * self.rampdown_proportion
        desired_step_interval = step_interval
        while is_moving:
            if steps_to_go > 0:
                current_time = time.time()
                if current_time - last_step_time >= step_interval:
                    if steps_to_go % 2 == 0:
                        GPIO.output(STEP_PIN, True)
                    else:
                        GPIO.output(STEP_PIN, False)

                    last_step_time = current_time
                    self.curr_position += step_direction
                    steps_to_go -= 1

                    # Determine the current step position relative to the total steps
                    steps_perfomed = total_steps - steps_to_go
                    current_speed = step_interval
                    #print(steps_perfomed)
                    # Apply soft start (ramp-up) at the beginning
                    if 0 < steps_perfomed <= initial_slow_steps:
                        ramp_up_factor = desired_speed / initial_slow_steps  # Transform speed to period
                        step_interval = 1 / (steps_perfomed * ramp_up_factor)
                    # Apply soft stop (ramp-down) at the end
                    elif (total_steps - final_slow_steps) < steps_perfomed <= total_steps:
                        steps_in = steps_perfomed - (total_steps - final_slow_steps)
                        ramp_down_factor = desired_speed / final_slow_steps  # Transform speed to period
                        speed = desired_speed - steps_in * ramp_down_factor
                        if speed != 0:
                            step_interval = 1 / speed
                        else:
                            step_interval = 100
                    # Continue with regular speed in between
                    else:
                        step_interval = desired_step_interval

            else:
                print("Movement has stopped.")
                is_moving = False
                time.sleep(1)
