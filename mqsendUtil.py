import stomp

# topic_name='/topic/interTopic'
def send_inter_topic(topic_name,ip,msg):
    conn=stomp.Connection([(ip,61613)])
    conn.start()
    conn.connect()
    try:
        print('mq发送给%s的消息为==%s'%(topic_name,msg))
        conn.send(destination=topic_name,body=msg)
    except Exception as e:
        print(e)
    conn.disconnect()


if __name__ == '__main__':
    topic_name = '/topic/interTopic'
    ip="10.12.4.132"
    send_inter_topic(topic_name,ip,'haha')