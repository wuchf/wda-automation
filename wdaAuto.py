from wdaUtil import wdacli
from loadUtil import *
from mqsendUtil import *
from validate import *

class uiautoTest():
    def __init__(self,post,bandid):
        self.wda=wdacli(post,bandid)


    def areaclick(self,value,kwargs):
        try:
            area=self.wda.findelement(kwargs)
            area.click()
            area_rect = area.bounds
            h = int(area_rect.height)
            area_origin = area_rect.center
            x = int(area_origin.x)
            y = int(area_origin.y)
            index=int(value)
            if index > 0:
                for i in range(index):
                    self.wda.swipe(x, y, y-h,y-h)
                self.wda.taphold_act(x, y)
            else:
                self.wda.taphold_act(x + h * index, y + h * index)
            return True
        except Exception as e:
            return False

    def execute(self,action,control,value):
        if action=='click':
            res=self.wda.click_act(control)
        elif action=='sclick':
            res=self.wda.sclick_act(value,control)
        elif action=='wclick':
            res=self.wda.wait_enabled_click(control,value)
        elif action=='cclick':
            res=self.wda.select_enabled_click(control,value)
        elif action=='sendkey':
            res=self.wda.sendkey(value,control)
        elif action=='taphold':
            res=self.wda.tap_hold(control)
        elif action=='swipe':
            res=self.wda.swipe_act(value,control)
        elif action=='sleep':
            res=self.wda.sleeptm(int(value))
        elif action=='select':
            res=self.areaclick(value,control)
        elif action=='alert':
            res=self.wda.alert(value)
        elif action=='gettext':
            res= self.wda.gettext(value,control)
        else:
            msg='执行失败，输入action错误，错误的action为=={}'.format(action)
            print(msg)
            res=False,msg
        return res

    def validate(self,value1,opera,value2,action):
        if action=='exist':
            return self.wda.exist_ele(value2)
        if action=='notexist':
            return not self.wda.exist_ele(value2)
        if action=='getvalue':
            _val=self.wda.gettext('value',value2)
            return check(value1,opera,_val)
        if action=='gettext':
            _val = self.wda.gettext('text', value2)
            return check(value1, opera, _val)
        else:
            return check(value1,opera,value2)



if __name__ == '__main__':
    con=load_file('../test.json')
    print(con)
    cases =con.get('testcases')
    print (cases)
    test=uiautoTest("com.tal100.DTSClassRoom")
    text =""
    for case in cases:
        for step in case['steps']:
            text=test.execute(step['action'],step['control'],step['value'])
        if case['mq']:
            send_inter_topic(case['mq'])


