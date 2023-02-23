from utils import *
import basicMove
import time
import rclpy


def count_time(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        func(*args, **kwargs)
        print('time ', time.time()-t)
    return wrapper


@count_time
def main():
    basicMove.movement(2, 0.4, 0.0, 0.6, yaxis=True)
    time.sleep(0.5)
    basicMove.movement(3, -0.4, 0.0, 0.2, yaxis=False)
    time.sleep(0.5)
    basicMove.movement(2, -0.4, 0.0, 0.4, yaxis=True, yaxis_stop_weight=7)
    for i in range(6):
        time.sleep(0.5)
        basicMove.movement(1, -0.4, 0.0, 0.4, yaxis=False)
    time.sleep(0.5)

    basicMove.movement(2, 0.4, 0.0, 0.4, yaxis=True)
    time.sleep(0.5)
    basicMove.movement(3, 0.4, 0.0, 0.4, yaxis=False)

    time.sleep(0.5)
    basicMove.movement(2, 0.4, 0.0, 0.78, yaxis=True)
    time.sleep(0.5)
    basicMove.movement(3, 0.0, -1.6, 0.0, yaxis=False)
    time.sleep(0.5)
    basicMove.movement(2, -0.4, 0.0, 0.4, yaxis=True, yaxis_stop_weight=6)
    for i in range(6):
        time.sleep(0.5)
        basicMove.movement(1, -0.4, 0.0, 0.4, yaxis=False)
    time.sleep(0.5)


if __name__ == '__main__':
    main()
