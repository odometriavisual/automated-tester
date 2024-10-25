import random

def generate_random_num(t, res=10, max=1000):
    # The same seed is considered every 'res' seconds.
    random.seed(t // res)
    return int(random.random() * max) # Between 0 and max