from motor import Motor

motor = Motor(min_position=-50000)

motor.move(2500, -10e3)
print(motor.curr_position)