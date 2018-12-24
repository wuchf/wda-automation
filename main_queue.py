import time
import logging

from wdaAuto import *
from mqsendUtil import send_inter_topic as send
from loadUtil import *
from reportUtil import *

topic_name='/topic/interTopic'
first=False #只有在第一次互动交互的时候进行验证，其他时间不需要

error=[] #保存用例步骤执行失败的用例名
fail=[] #保存用例验证失败的用例名
success=[]#保存用例执行成功的用例名（步骤执行成功，验证通过)
skip=[]#保存没有被执行的用例（包含tm为0的用例和skipif中需要跳过的用例)

def run(fn,ip,case,queue,pipe,res=[],check_res=[]):
    global first
    logging.info("是否在第一次执行互动=={}".format(first))
    #有mq的地方，就是互动的交互，需要等待互动端已经初始化完成
    if case['mq']:
        while first:
            if not queue.empty():
                # _msg=queue.get()#queue中的信息取出
                logging.info("queue是否为空=={} ".format(queue.empty()))
                first=False
        #将给互动发消息的mq生产指令和用例执行分开
        # queue.put(case['mq'])
        send(topic_name, ip, case['mq'])
        # time.sleep(60)  ##开启之后等待时间，需要设置为配置文件
    if case['pipe']:
        pipe.send(case['mq'])
    for step in case['steps']:
        _res = fn.execute(step['action'], step['control'], step['value'])
        res.append(_res)
    if len(res)==len([x for x in res if x==True]):  # 如果都执行成功

        if case['validate']:  # 有验证的信息
            for _validate in case['validate']:
                _check=fn.validate(_validate['value1'],_validate['operation'],_validate['value2'],_validate['action'])
                check_res.append(_check)
        else:
            check_res.append(True)
            # success.append(case['name'])

    else:
        error.append((case['name'],[x for x in res if x !=True]))

def autotest(conf,cases,slptms,queue,pipe):

    # 编译xcode
    # iproxy指令
    tm_start=time.time()
    test = uiautoTest(conf['port'],conf['bandid'])
    for case in cases:
        logging.info('{}执行的用例编号为=={}，用例名称为=={}'.format(conf['name'],case['no'],case['name']))
        res=[]#保存步骤执行结果
        check_res=[]#保存验证结果
        if case['tm']:
            tm=int(case['tm'])
        else:
            tm=1
        if tm==0:#如果tm为0，就直接跳过不执行
            skip.append((case['name'],"执行次数为0，跳过"))
        for i  in range(tm):
            if not case['skipif']:#无执行用例的条件
                run(test,conf['mqip'],case,queue,pipe,res,check_res)
            else:
                _skip_res=[]
                for _skip in case['skipif']:
                    #对于执行用例条件，可以判断已经执行过的用例名称，一执行过的用例执行通过了或者失败了才会运行
                    if _skip['operation'] in ['notin','ni']:
                        _res=_skip['value1'] not in success
                    elif _skip['operation'] in ['in']:
                        _res=_skip['value1'] in success
                    else:
                        _res=test.validate(_skip['value1'],_skip['operation'],_skip['value2'],_skip['action'])
                    _skip_res.append(_res)
                logging.info('{}运行skipif 后的结果为{}'.format(conf['name'],_skip_res))
                if len(_skip_res)==len([x for x in _skip_res if x==True]):#不执行条件都成功了，直接跳过不运行
                    skip.append((case['name'],'{}运行skipif 后的结果为{},跳过'.format(case['name'],_skip_res)))
                else:
                    run(test, conf['mqip'], case, queue,pipe, res, check_res)
            #没有跳过，执行等待时间操作
            if case['name'] not in [x[0] for x in skip] and case['name'] not in [x[0]for x in error]:
                #在配置sleeptime（冷冻时间）中查看，有无和用例名相同的冷冻时间，如果有，进行相应时间的冷冻,如果没有，使用默认冷冻时间
                t=[x['time'] for x in slptms if x['name']==case['name']]
                if t:
                    time.sleep(t[0])
                else:
                    time.sleep([x['time'] for x in slptms if x['name']=='默认冷冻'][0])

        # if not all(check_res):
        if len(check_res)!=len([x for x in check_res if x==True]):
            fail.append((case['name'],[x for x in check_res if x!=True]))
        #步骤都成功，验证都成功，用例执行成功
        #当用例skip之后，case 的name会在skip钟，需处理
        if len(res)==len([x for x in res if x==True]) and len(check_res)==len([x for x in check_res if x==True]) and case['name'] not in [x[0] for x in skip]:
            success.append(case['name'])

    #所有的用例执行完之后，发送结束指令给mq发送端
    print("queue添加信息==结束")
    queue.put("结束")
    tm_end=time.time()
    print(f'{conf["name"]}执行成功=={success}')
    print(f'{conf["name"]}执行失败=={error}')
    print(f'{conf["name"]}验证失败=={fail}')
    print(f'{conf["name"]}跳过不执行=={skip}')
    _result={"success":success,"error":error,"fail":fail,"skip":skip}
    print(_result)
    # return {"success": success, "error": error, "fail": fail, "skip": skip}
    fp = open("teacher_result.html", 'wb')
    tm = tm_end-tm_start
    res = result(tm, fp, title="UI自动化测试报告", teacherpad=_result)
    # result()
    res.generatereport()
if __name__ == '__main__':
    # filename='../testdemo.json'
    filename = '../teacher.json'
    con = load_file(filename)
    cases = con.get('testcases')
    conf = con.get('config')
    sleeptime=con.get('sleeptime')
    logging.info(conf)
    logging.info(sleeptime)
    queue=""
    pipe=""
    autotest(conf,cases,sleeptime,queue,pipe)