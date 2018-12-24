import psutil
import os
import requests
import time
from threading import Lock
lock=Lock()

def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton
# @Singleton
class WDAserver(object):
    instance = None


    def __init__(self,port,uuid):
        self.port=port
        self.uuid=uuid
        self.xcodebuild_exe='/usr/bin/xcodebuild'
        self.iproxy_exe='/usr/local/bin/iproxy'
        self.wda_project='/Users/weilai/Desktop/WebDriverAgent/WebDriverAgent.xcodeproj'
        self.wda_schema='WebDriverAgentRunner'
        self.wda_configuration='Debug'
        self.xcodebuild_log='/usr/local/var/log/%s-build.log'%self.port
        self.iproxy_log='/usr/local/var/log/%s-iproxy.log'%self.port
        self.server_url='http://localhost:%s/status'%port
        self.timeout=300
        self.xcodebuild_cmd= 'xcodebuild -project /Users/weilai/Desktop/WebDriverAgent/WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination "id=%s" test >%s 2>& 1' % (self.uuid,self.xcodebuild_log)
        self.iproxy_cmd="%s %s 8100 %s >%s 2>& 1"%(self.iproxy_exe,self.port,self.uuid,self.iproxy_log)
    @classmethod
    def get_instance(cls):
        if cls.instance:
            return cls.instance
        else:
            obj=cls(cls.port,cls.uuid)
            cls.instance=obj
            return obj
    def restart(self):
        with lock:
            os.popen(self.iproxy_cmd)
            os.popen(self.xcodebuild_cmd)
            _res=self.wait_until_isrunning(self.timeout)
            print(_res)
            return _res


    def wait_until_isrunning(self,timeout):
            tm_start=time.time()
            while True:
                try:
                    code=requests.get(self.server_url).status_code
                except:
                    code=0
                    pass

                # print(code)
                if code==200:
                    print("wda在%s秒钟启动成功"%(time.time()-tm_start))
                    return True
                else:
                    time.sleep(2)
                    # print(time.time()-tm_start)
                    if time.time()-tm_start>timeout:
                        print("wda启动失败")
                        return False

    def isrunning(self,processname):
        pids=psutil.pids()
        for pid in pids:
            if psutil.Process(pid).name()==processname:
                return True
        return False

    def killpid(self,processname):
        pids = psutil.pids()
        try:
            for pid in pids:
                if psutil.Process(pid).name() == processname:
                    print ("存在程序%s，pid为：%s"%(processname,pid))
                    psutil.Process(pid).kill()
        except:
            pass

    # def  callback(self,func):



if __name__ == '__main__':

    port='8200'
    uuid='617c65dc4aa1b78ef621620667a5c59a5b934dfa'
    wda=WDAserver(port,uuid)
    wda.restart()








