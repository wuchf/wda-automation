import atexit

import stomp
import time
import logging

from mqsendUtil import send_inter_topic as send
reback_topic='/topic/rebackTopic' #互动端的返回
inter_topic='/topic/interTopic'  #给互动端发送的信息


class SampleListener(stomp.ConnectionListener):
    def __init__(self,conn,ip,queue):
        self.conn=conn
        self.ip=ip
        self.q=queue

    def on_message(self, headers, body):
        logging.info(f'从互动端收到的反馈信息为 =={body}')
        if self.q.full():
            print("结束运行，退出")
            # 如果queue队列已经满了，就发送结束指令给互动端
            send(inter_topic, self.ip, 'stop')
            # 断开mq连接
            self.conn.term = True
        if body=='beginok':
            send(inter_topic,self.ip,'启动')
        if body=='启动ok':
            send(inter_topic, self.ip,'登录')
        if body=='登录ok':
            send(inter_topic, self.ip,'初始化')
            # send(inter_topic, self.ip, 'stop')
        if body=='初始化ok':
            print("queue添加信息ok")
            self.q.put('ok')
        if body == '初始化fail':
            self.q.put('ok')

    def on_error(self, headers, body):
        logging.info(f'[{body}] recevied an error')

    def on_disconnected(self):
        self.conn.disconnect()

#mq不停止
def recv_from_topic(ip,queue):
    conn=stomp.Connection([(ip,61613)])
    conn.set_listener('',SampleListener(conn,ip,queue))
    conn.start()
    conn.connect()
    logging.info('等待互动端的返回')
    conn.subscribe(destination=reback_topic,id='1')
    while True:
        pass


class amqconnect(object):
    def __init__(self,ip,queue):
        self.conn = stomp.Connection([(ip, 61613)])
        self.conn.set_listener('', SampleListener(self, ip, queue))
        self.conn.start()
        self.conn.connect()
        logging.info('等待互动端的返回')
        self.conn.subscribe(destination=reback_topic, id='1')
        atexit.register(self.close)
        self.term=False

    def run_forver(self):
        while not self.term:
            time.sleep(5)

    def close(self):
        self.conn.disconnect()
        logging.info("mq连接断开了")


def run(ip,q):
    send(inter_topic,ip, 'begin')
    amq=amqconnect(ip,q)
    amq.run_forver()
    # recv_from_topic(ip,q)

if __name__ == '__main__':
    ip=""
    q=""
    run(ip,q)