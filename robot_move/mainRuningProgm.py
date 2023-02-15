from utils import *
import basicMove
import time


def count_time(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        func(*args, **kwargs)
        print('time ', time.time()-t)
    return wrapper


@count_time
def main(args=None):
    # basicMove.getPose()
    basicMove.movement(0.2, 0, 0.4)
    # time.sleep(10)
    # basicMove.basicMove(-0.4,0,3)


if __name__ == '__main__':
    main()
