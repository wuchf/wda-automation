import stomp
import time

from mqsendUtil import send_inter_topic as send
reback_topic='/topic/rebackTopic' #互动端的返回
inter_topic='/topic/interTopic'  #给互动端发送的信息


class SampleListener(stomp.ConnectionListener):
    def __init__(self,conn,ip):
        self.conn=conn
        self.ip=ip

    def on_message(self, headers, body):
        print(f'message is =={body}')
        if body=='beginok':
            send(inter_topic,self.ip,'启动')
        if body=='启动ok':
            send(inter_topic, self.ip,'登录')
        if body=='登录ok':
            send(inter_topic, self.ip,'初始化')
        if body=='初始化ok':
            pass


    def on_error(self, headers, body):
        print(f'[{body}] recevied an error')

    def on_disconnected(self):
        self.conn.disconnect()

def recv_from_topic(ip):
    conn=stomp.Connection([(ip,61613)])
    conn.set_listener('',SampleListener(conn,ip))
    conn.start()
    conn.connect()
    print('等待互动端的返回')
    conn.subscribe(destination=reback_topic,id='1')
    while True:
        pass

def run(ip):
    send(inter_topic,ip, 'begin')
    recv_from_topic(ip)

if __name__ == '__main__':
    ip=""
    run(ip)