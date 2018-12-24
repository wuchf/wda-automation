import wda
import time
from PIL import Image
import requests
requests.adapters.DEFAULT_RETRIES=5
import retry
import logging
wda.DEBUG=False   #默认为false
wda.HTTP_TIMEOUT =600 #默认为60s

class wdacli():

    def __init__(self,post,bandid):
        try:
            self.client = wda.Client("http://localhost:%s"%post)
            print(self.client.status())#获取状态
            # self.client.wait_ready(timeout=300)  #等待wda完成，默认超时时间为120s
            # self.client.home()##按home键
            self.client.home()
            self.client.healthcheck()
            self.session = self.client.session(bandid)
            # self.session = self.con(bandid)
            # self.session.orientation
            # self.session.set_alert_callback()
        except  Exception as e:
            logging.error ("启动wda失败，失败原因为==",e)
            # time.sleep(5)
            # self.session = self.client.session(bandid)
        time.sleep(5)
    @retry.retry(tries=10,delay=10)
    def con(self,bandid):
        session= self.client.session(bandid)
        logging.info("获得的session为%s"%session)
        return session

    def findelement(self,kwargs):
        """
        查找元素
        :param kwargs: 查找的信息，如ClassName='textfiled',name='muban'
        :return: 返回元素
        """
        predicate = id = className = name = nameContains = nameMatches = value = valueContains =xpath= label=labelContains = visible = enabled = classChain = xpath = None
        index = 0
        element=None
        for _ele in kwargs.split(','):
            _e=_ele.split('=')
            if _e[0].lower()=='id':
                id=_e[1]
            elif _e[0].lower() in ['name','n']:
                name=_e[1]
            elif _e[0].lower() in ['namecon','namecontains','namecontain']:
                nameContains=_e[1]
            elif _e[0].lower() in ['namemat','namematch','namematches']:
                nameMatches=_e[1]
            elif _e[0].lower() in ['classname','clsn']:
                className=_e[1]
            elif _e[0].lower() in ['value','v']:
                value=_e[1]
            elif _e[0].lower() in ['valuecon','valuecontains','valuecontain']:
                valueContains=_e[1]
            elif _e[0].lower() in ['label','l']:
                label=_e[1]
            elif _e[0].lower() in ['labelecon','labelcontains','labelcontain']:
                labelContains=_e[1]
            elif _e[0].lower() in ['xpath']:
                xpath=_e[1]
            elif _e[0].lower() in ['chain']:
                classChain=_e[1]
            elif _e[0].lower() in ['visible']:
                visible=_e[1]
            elif _e[0].lower() in ['enable','enabled']:
                enabled=_e[1]
            elif _e[0].lower() in ['index']:
                index=int(_e[1])
            else:
                logging.error('元素定位信息错误,错误信息为=={}'.format(_e[0]))
        try:

            element=self.session(predicate=None,
            id=id,className=className,
            name=name, nameContains=nameContains, nameMatches=nameMatches,
            value=value, valueContains=valueContains,
            label=label, labelContains=labelContains,
            visible=visible, enabled=enabled,
            classChain=classChain,
            xpath=xpath,index=index)
        except Exception as e:
            logging.error('{}元素找不到'.format(kwargs))
            raise e
        return element
    def exist_ele(self,kwargs):
        return self.findelement(kwargs).exists
        #
        # _el=self.findelement(kwargs).find_elements()
        # logging.info('元素信息为=={}'.format(_el))
        # if _el:
        #     return True
        # else:
        #     return False
    def sendkey(self,value,kwargs):
        """
        输入信息
        :param value: 输入的值
        :param kwargs: 输入的元素定位信息
        :return: 无
        """
        element=self.findelement(kwargs)
        try:
            element.clear_text()
            element.set_text(value)
            return True
        except Exception as e:
            msg='【{}】执行sendkey操作失败，失败原因=={}'.format(kwargs,e)
            logging.error(msg)
            return msg

    def click_act(self,kwargs):
        """
        单击操作
        :param kwargs: 单击的元素信息
        :return:
        """
        try:
            self.findelement(kwargs).tap()
            return True
        except Exception as e:
            msg="【{}】执行click操作失败，失败原因=={}".format(kwargs,e)
            logging.error(msg)
            return msg


    def taphold_act(self,x,y,duration=1.0):
        """

        :param x:
        :param y:
        :param duration:
        :return:
        """
        try:
            self.session.tap_hold(x,y,duration)
            return True
        except Exception as e:
            msg='执行taphold操作失败，失败原因=={}'.format(e)
            logging.error (msg)
            return msg

    def tap_hold(self,kwargs):
        try:
            center=self.getcenter(kwargs)
            x=int(center.x)
            y=int(center.y)
            # return self.taphold_act(x,y)
            self.session.tap_hold(x, y, duration=1)
            return True
        except Exception as e:
            msg='【{}】执行tap_hold操作失败，失败原因=={}'.format(kwargs,e)
            logging.error(msg)
            return msg

    def sclick_act(self,value,kwargs):
        """
        单击操作,现进行下滑，然后在单击
        :param kwargs: 单击的元素信息
        :return:
        """
        try:
            self.swipe_act(value,"")
            self.tap_hold(kwargs)
            # self.findelement(kwargs).tap()
            return True
        except Exception as e:
            msg="【{}】执行sclick_act操作失败，失败原因=={}".format(kwargs,e)
            logging.error(msg)
            return msg

    def wait_enabled_click(self,kwargs,value):
        start_time = time.time()
        try:
            if value == 'enable':
                while start_time + 60 > time.time():
                    enable=self.findelement(kwargs).find_elements()[0].enabled
                    logging.info (f"{kwargs}元素是否为enable=={enable}")
                    if enable:
                        self.click_act(kwargs)
                        return True
                    time.sleep(1)
            elif value=='exist':
                # self.findelement(kwargs).click_exists(timeout=60)
                while start_time + 60 > time.time():
                    res=self.exist_ele(kwargs)
                    logging.info(f"{kwargs}元素是否存在=={res}")
                    if res:
                        self.click_act(kwargs)
                        return True
                    time.sleep(1)
        except Exception as e:
            msg="【{}】执行wait_enabled_click操作失败，失败原因=={}".format(kwargs,e)
            logging.error (msg)
            return msg

    def select_enabled_click(self,kwargs,value):
        try:
            element=self.findelement(kwargs).find_elements()
            num=int(value) if value!="" else 1
            for _ele in element:
                enable=_ele.enabled
                visible=_ele.visible
                print("元素的enable属性为%s"%enable)
                if enable and visible:
                    _ele.tap()
                    num = num - 1
                    print (num)
                    if num<=0:
                        break
            return True
        except Exception as e:
            msg="【{}】执行select_enabled_click操作失败，失败原因=={}".format(kwargs,e)
            logging.error(msg)
            return msg

    def scroll_act(self,kwargs):
        '''
        滚动屏幕，到指定元素出现
        :param kwargs: 元素定位信息
        :return:
        '''
        try:
            self.findelement(kwargs).scroll()
            return True
        except Exception as e:
            msg='【{}】执行scroll操作失败，失败原因=={}'.format(kwargs,e)
            logging.error (msg)
            return msg

    def swipe_act(self,value,kwargs):
        try:
            if value=='up':
                self.session.swipe_up()
            elif value=='down':
                self.session.swipe_down()
            elif value=='left':
                self.session.swipe_left()
            elif value=='right':
                self.session.swipe_right()
            elif value=='center_up':
                w,h=self.session.window_size()
                self.session.swipe(w/2, h/2, w/2, 0)
            elif value=='center_down':
                w,h=self.session.window_size()
                self.session.swipe(w/2, h/2, w/2, h)
            elif value=='center_left':
                w,h=self.session.window_size()
                self.session.swipe(w/2, h/2, 0, h/2)
            elif value=='center_right':
                w,h=self.session.window_size()
                self.session.swipe(w/2, h/2, w, h/2)
            elif(''.join(value.split(',')).isdigit() and ''.join(kwargs.split(',')).isdigit()):
                #输入两个元素位置或者指定起始，结束点
                first=value.split(',')
                second=kwargs.split(',')
                self.session.swipe(int(first[0]),int(first[1]),int(second[0]),int(second[1]),duration=1)
            elif(''.join(value.split(',')).isdigit()):
                point=value.split(',')
                center = self.getcenter(kwargs)
                x = int(center.x)
                y = int(center.y)
                self.session.swipe(x, y,int(point[0]),int(point[1]),duration=1)
            elif(''.join(kwargs.split(',')).isdigit()):
                point = kwargs.split(',')
                center = self.getcenter(value)
                x = int(center.x)
                y = int(center.y)
                self.session.swipe(int(point[0]), int(point[1]),x,y,duration=1)
            return True
        except Exception as e:
            msg='【{}】执行swipe操作失败，失败原因为=={}'.format(kwargs,e)
            logging.error (msg)
            return msg
    def swipe(self,x1,y1,x2,y2,duration=1):
        self.session.swipe(x1,y1,x2,y2,duration)
    def getrect(self,kwargs):
        '''
        获取元素的位置
        :param kwargs: 元素信息
        :return: Rect(x={x}, y={y}, width={w}, height={h})
        '''
        try:
            return self.findelement(kwargs).bounds
        except Exception as e:
            msg="【{}】执行getrect操作失败，失败原因=={}".format(kwargs,e)
            logging.error(msg)
            return msg

    def getcenter(self,kwargs):
        '''
        获取元素的中心位置
        :param kwargs:
        :return: namedtuple('Point', ['x', 'y'])
        '''
        try:
            return self.getrect(kwargs).center
        except Exception as e:
            msg="【{}】执行getcenter操作失败，失败原因=={}".format(kwargs,e)
            logging.error(msg)
            return msg

    def gettext(self,val,kwargs):
        try:
            if val=='text':
                _val=self.findelement(kwargs).text
            elif val=='value':
                _val=self.findelement(kwargs).value
            else:
                _val=None
            logging.info("获取元素%s的%s的值为：%s" % (kwargs,val,_val))
            return _val
        except Exception as e:
            msg="【{}】执行gettext操作失败，失败原因=={}".format(kwargs,e)
            logging.error(msg)
            return msg

    def capture(self,name):
        '''
        截屏
        :param name: 保存的名称
        :return:
        '''
        try:
            self.session.screenshot().save(name)
            # self.client.screenshot(name)
            return True
        except Exception as e:
            logging.error("执行capture操作失败，失败原因=={}".format(e))
            return False

    def sleeptm(self,sec):
        '''
        冷冻时间
        :param sec: 时间，单位为秒
        :return:
        '''
        time.sleep(sec)
        return True

    def alert(self,value,timeout=15):
        '''
        处理alert消息
        :param value: ok或者no或者指定的元素的button的name值
        :return:
        '''
        start_time = time.time()
        try:
            while start_time + timeout > time.time():
                if value=='ok':
                    self.session.alert.accept()
                elif value=='no':
                    self.session.alert.dismiss()
                else:
                    self.session.alert.click(value)
                return True
        except Exception as e:
            msg="处理alert操作失败，失败原因=={}".format(e)
            logging.error (msg)
            return msg

    def capture_xy(self,name,**kwargs):
        '''
        保存指定区域中的图片
        :param name: 保存图片的名称
        :param kwargs: 元素信息
        :return:
        '''
        rect=self.getrect(**kwargs)
        x=rect.x
        y=rect.y
        h=rect.height
        w=rect.width
        self.capture(name)
        Image.open(name).crop((x,y,y+h,x+w)).save(name)

if __name__ == '__main__':
    test = wdacli("com.tal100.DTSClassRoom")
    test.sendkey('testz0055',no=1,control='className=TextField')
    test.capture_xy('name12.png',no=1,control='className=TextField')