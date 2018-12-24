import multiprocessing
import threading
from queue import Queue

from main_tutor import autotest
from mqrecvUtil import run
from loadUtil import *

if __name__ == '__main__':
    # filename = '../testdemo.json'
    # con = load_file(filename)
    # cases = con.get('testcases')
    # conf = con.get('config')
    # print(conf)
    # ip=conf['mqip']
    # p1=multiprocessing.Process(target=run,args=(ip,))
    # p2=multiprocessing.Process(target=autotest,args=(conf,cases,))
    # p1.start()
    # p2.start()
    queue=Queue(maxsize=1000)
