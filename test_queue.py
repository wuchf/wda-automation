from multiprocessing import Pool,Process,Pipe
import threading
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess
from queue import Queue
import time
import sys
import logging
import requests

from main_queue import autotest
from main_tutor import autotest as tutor_test
from mqrecvUtil_queue import run
from loadUtil import *
from WDAserver import *

LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='log.txt',level=logging.DEBUG,format=LOG_FORMAT)


class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def teacher(pipe):
    queue = Queue(maxsize=2)#设置大小为2，一个是用来存储互动端之后初始化完成的信息，另一个用来存储脚本执行完成的信息
    t1 = threading.Thread(target=run, args=((ip, queue,)))
    t2 = threading.Thread(target=autotest, args=(teacher_conf, teacher_cases, teacher_sleeptime, queue, pipe))
    t1.start()
    t2.start()
    queue.join()
    # t=[]
    # t1 = MyThread(func=run, args=((ip, queue,)))
    # t.append(t1)
    # t2 = MyThread(func=autotest, args=(teacher_conf, teacher_cases, teacher_sleeptime, queue, pipe))
    # t.append(t2)
    # for i in t:
    #     t[i].start()
    # for i in t:
    #     t[i].join()
    #
    # print( t2.get_result())


if __name__ == '__main__':
    teacher_init=None
    tutor_init=None
    teacher_file = '../teacher.json'
    teacher_info = load_file(teacher_file)
    teacher_cases = teacher_info.get('testcases')
    teacher_conf = teacher_info.get('config')
    teacher_sleeptime = teacher_info.get('sleeptime')
    logging.info(teacher_conf)
    logging.info(teacher_sleeptime)
    ip = teacher_conf['mqip']
    teacher_uuid = teacher_conf['uuid']
    teacher_port = teacher_conf['port']
    cmd = 'instruments -s devices'
    d = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    outs = d.stdout.readlines()
    logging.info(outs)
    res = [x for x in outs if teacher_uuid in x.decode('utf-8')]
    logging.info(res)
    if not res:
        logging.info("设备%s未连接到电脑，请使用usb连接" % teacher_uuid)
        sys.exit(1)


    tutor_filename = '../tutor.json'
    tutor_info = load_file(tutor_filename)
    tutor_cases = tutor_info.get('testcases')
    tutor_conf = tutor_info.get('config')
    tutor_sleeptime = tutor_info.get('sleeptime')
    logging.info(tutor_conf)
    logging.info(tutor_cases)
    logging.info(tutor_sleeptime)
    tutor_port = tutor_conf['port']
    tutor_uuid = tutor_conf['uuid']
    d = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    outs = d.stdout.readlines()
    res = [x for x in outs if tutor_uuid in x.decode('utf-8')]
    logging.info(res)
    wda = WDAserver(teacher_port, teacher_uuid)
    wda.killpid("xcodebuild")
    wda.killpid("iproxy")
    _tea=wda.restart()
    print("主讲端启动wda 的结果为：%s" % _tea)
    wda1=WDAserver(tutor_port,tutor_uuid)
    _tutor=wda1.restart()
    # if wda.isrunning()

    print("辅导端启动wda的结果为：%s" % _tutor)
    if all([_tea,_tutor]):
        time.sleep(3)
        pipe = Pipe()
        p1=Process(target=teacher,args=(pipe[0],))
        p2=Process(target=tutor_test, args=(tutor_conf,tutor_cases,tutor_sleeptime,pipe[1],))
        p2.start()
        p1.start()
        p1.join()
        p2.join()
    else:
        print("主讲或则辅导wda启动失败，程序不运行")

        # # p=Pool(2)
        # # res1=p.apply_async(teacher,args=(pipe[0],))
        # # res2=p.apply_async(tutor_test,args=(tutor_conf,tutor_cases,tutor_sleeptime,pipe[1],))
        # # print(res1.get())
        # # print(res2.get())
        # teacher(pipe[0])




