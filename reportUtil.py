# -*- coding: utf-8 -*
import sys
import os

HTML_TMP = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.bootcss.com/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script src="http://cdn.hcharts.cn/highcharts/highcharts.js"></script>
    <style type="text/css">
        #chart{
            width: 550px;
            height: 500px;
            margin: 0;
        }
        .error{
            color: red;
            font-weight:bold
            }
        .pass{
            color: green;
            font-weight:bold
            }
        .fail{
            color: orange;
            font-weight:bold
            }
        .skip{
            color: gray;
            font-weight:bold
            }
        .content{
            padding:100px;
        }
        td{
            {#max-width: 80px;#}
            word-wrap: break-word;
            table-layout:fixed;
            word-break:break-all;
        }
    </style>
    <title>%(title)s</title>
</head>
<body>
%(script)s
%(body)s
</body>
'''
HTML_SCRIPT = '''
<script language="JavaScript">
    $(document).ready(function() {  
   var chart = {
       plotBackgroundColor: null,
       plotBorderWidth: null,
       plotShadow: false
   };
   var title = {
      text: '测试统计数据'   
   };      
   var tooltip = {
      pointFormat: '{series.name}：{point.percentage:.2f}%%'
   };
   var plotOptions = {
      pie: {
         allowPointSelect: true,
         cursor: 'pointer',
         dataLabels: {
            enabled: true,
            format: '<b>{point.name}</b>: {point.percentage:.2f}%%',
            style: {
               color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
            }
         }
      }
   };
   var series= [{
      type: 'pie',
      name: '比例',
      data: [
       ['fail',    %(fail)d],
       ['error',   %(error)d],
       ['skip',    %(skip)d],
         {
            name: 'success',
            y: %(success)d,
            sliced: true,
            selected: true
         },
      ]
   }];     

   var json = {};   
   json.chart = chart; 
   json.title = title;     
   json.tooltip = tooltip;  
   json.series = series;
   json.plotOptions = plotOptions;
   $('#chart').highcharts(json);  
   
   $('#all').find('table').find('tr').on('click', function(e){
        e.preventDefault();
        $(this).next('tr.content').toggle()
    }); 
});

</script>

'''
HTML_BODY = '''
<div class="container" >
<h2>UI自动化测试报告</h2>
    <div class="col-md-12">
        <div class="col-md-3">
            <h3>测试概要信息</h3>
            <p> 总计运行时间：%(time)s</p>
            <p> 用例成功数：%(success)s</p>
            <p> 用例失败数：%(error)s</p>
            <p> 用例验证失败数：%(fail)s</p>
            <p> 未验证：%(skip)s</p>
        </div>
        <div class="col-md-9">
            <div id="chart" style="width: 550px; height: 300px; margin: 0 auto"></div>
        </div>
    </div>
    <div id='all'>
    <h3>详细信息</h3>
        <table class="table table-striped table-bordered table-hover" width="100">
                <th >平台名称</th>
                <th >pass</th>
                <th>error</th>
                <th >fail</th>
                <th >skip</th>
                %(tr)s
        </table>
    </div>
    </div>
'''

TABLE_INFO = '''
    <tr class="active">
        <td width="10%%">%(case)s</td>
        <td width="10%%"class="pass">%(pass)s</td>
        <td width="10%%"class="error">%(error)s</td>
        <td width="10%%"class="fail">%(fail)s</td>
        <td width="10%%"class="skip">%(skip)s</td>
    </tr>
    <tr class='content' style="display: none"><td colspan="6">%(detail)s</td></tr>
'''

DETAIL_INFO='''
    <table class="table table-striped table-bordered" width="100">
        <caption>平台端%(platform)s的结果</caption>
        <tr>
            <td class="pass">执行成功用例：</td><td width="80%%" class="pass">%(success)s</td>
        </tr>
        <tr>
            <td class="error">执行失败用例：</td><td width="80%%" class="error">%(error)s</td>
        </tr>
        <tr>
            <td class="fail">验证失败用例：</td><td width="80%%" class="fail">%(fail)s</td>
        </tr>
        <tr>
            <td class="skip">未执行用例：</td><td width="80%%" class="skip">%(skip)s</td>
        </tr>
        %(img)s
    </table>

'''
IMG_INFO='''
    <tr>
        <td>
            <img  name="pic" src="%s" height="200" width="200"/>
        </td>
    </tr>
'''
RESULT_HEAD="""
    <table class="table table-striped table-bordered" width="50">
    <th width="20%%">用例名称</th>
    <th width="80%%">失败原因</th>
    %s
    </table>
"""
RESULT_INFO="""
    <tr>
        <td>
            %s
        </td>
        <td>
            %s
        </td>
    </tr>
"""

class result():
    DEFAULT_TITLE = '测试报告'
    # teacher = None, tutor = None, student = None, tea_pc = None,
    def __init__(self,time, stream=sys.stdout, title=None,**kwargs):
        self.stream = stream
        if title:
            self.title = title
        else:
            self.title = self.DEFAULT_TITLE
        self.time = time
        self.results=kwargs
        self.success=0
        self.fail=0
        self.skip=0
        self.error=0
        self.ans=0
        # print(self.results)

    def detail(self):
        details=[]
        for plat, res in self.results.items():
            info={}
            # if res["fail"]!=0:
            #     path="D:\\work\\result\\%s"%plat
            #     imgs=[]
            #     for i in {x:y for x,y in v.items() if y == "fail"}:
            #         f_list = os.listdir(path)
            #         for l in f_list:
            #             if l.startswith(name+"-"+i):
            #                 img=IMG_INFO%(path+"\\"+l)
            #         imgs.append(img)
            #     info["img"]="".join(imgs)
            # else:
            #     info["img"]=""
            _su = res.get("success")
            _error = res.get("error")
            _fail = res.get("fail")
            _skip = res.get("skip")
            if _su:
                _case=[]
                for case in _su:
                    _ca=RESULT_INFO%(case,"")
                    _case.append(_ca)
                info['success']=RESULT_HEAD%"".join(_case)
            else:
                info["success"]=""
            if _error:
                _case=[]
                for case,msg in _error:
                    _ca=RESULT_INFO%(case,'<hr/>'.join(msg))
                    _case.append(_ca)
                info["error"]=RESULT_HEAD%"".join(_case)
            else:
                info["error"]=""
            if _fail:
                _case = []
                for case, msg in _fail:
                    _ca = RESULT_INFO % (case, '<hr/>'.join(msg))
                    _case.append(_ca)
                info["fail"] = RESULT_HEAD%"".join(_case)
            else:
                info["fail"]=""
            if _skip:
                _case = []
                for case, msg in _skip:
                    _ca = RESULT_INFO % (case, msg)
                    _case.append(_ca)
                info["skip"] = RESULT_HEAD%"".join(_case)
            else:
                info["skip"]=""
            info["platform"]=plat
            info["img"]=""
            detail=DETAIL_INFO%info
            details.append(detail)
        return details

    def _generate_data(self):
        # 所有信息
        rows = []
        # for i in self.cases:
        info={"case":"","pass":0,"fail":0,"error":0,"skip":0}
        # info["num"]=self.answers[i]
        info["detail"]=''.join(self.detail())
        for plat, res in self.results.items():
            _su=res.get("success")
            _error=res.get("error")
            _fail=res.get("fail")
            _skip=res.get("skip")
            info["case"]=plat
            info["pass"]=len(_su)
            info["error"] = len(_error)
            info["fail"] = len(_fail)
            info["skip"] = len(_skip)
        self.success += info["pass"]
        self.error += info["error"]
        self.fail += info["fail"]
        self.skip += info["skip"]
        row = TABLE_INFO % info
        rows.append(row)
        body = HTML_BODY % dict(
            tr=''.join(rows),
            # title=self.title,
            time=self.time,
            success=self.success,
            fail=self.fail,
            error=self.error,
            skip=self.skip,
        )
        return body


    def chart(self):
        total=self.skip+self.fail+self.success+self.error
        chart = HTML_SCRIPT % dict(
            fail=self.fail/ total * 100,
            success=self.success / total * 100,
            skip=self.skip / total * 100,
            error=self.error/total*100,
        )
        return chart

    def generatereport(self):
        output = HTML_TMP % dict(
            title=self.title,
            body=self._generate_data(),
            script=self.chart()
        )
        self.stream.write(output.encode('utf-8'))
        self.stream.flush()

    def generaterdetail(self,name):
        a={}
        for plat,res in self.results.items():
            for k,v in res.items():
                if k==name:
                    a[plat]=v

    def getfile(self,path,pre):
        f_list = os.listdir(path)
        for l in f_list:
            if l.startswith(pre):
                print (l)





if __name__ == '__main__':
    fp = open("result.html", 'wb')
    time = '0.12'
    # results=[{'name': 'login', 'seqid': 1, 'expect': "'status','200'", 'result': 'fail', 'response': '{"avatar":null,"businessId":"40288b155f4d4c0c015f4d9a2eef00d1","userType":"2","loginName":"xiangjiaopi","token":"fab340e5229f4dc48e95ea583abd18cd","point":0,"areaCode":"020","areaName":"广州","liveNum":null,"classId":null,"classNum":null,"yunXinId":"40288b155f4d4c0c015f4d9a2eef00d1","yunXinToken":"9c0d6e6ec1ba4921a9677813000e7e03","stuNum":0}'}, {'name': 'login', 'seqid': 2, 'expect': '1000', 'result': 'pass', 'response': '{"message":"用户名或密码错误","status":"error"}'}]
    teacherpc = {"login": {"login": "pass"},
                 "zuoti": {"title": "pass", "pre-finish": "pass", "pre-answer1": "fail", "finish": "fail",
                           "answer1": "skip"}}
    studentpc = {"login": {"login": "pass"},
                 "zuoti": {"title": "pass", "tip": "pass", "pre_progress": "fail", "progress": "skip"}}
    teacher = {"login": {"login": "pass"}, "zuoti": {"open": "pass", "finish": "fail"}}
    tutor = {'success': ['登录'], 'error': [('做题关闭', ['name=结束执行click操作失败，失败原因==element not found', '处理alert操作失败，失败原因==WDAError(status=27, value={})']), ('轻选择题关闭', ["name=A执行tap_hold操作失败，失败原因=='tuple' object has no attribute 'x'", 'name=公布答案执行click操作失败，失败原因==element not found']), ('发积分关闭', ['name=结束执行click操作失败，失败原因==element not found', '处理alert操作失败，失败原因==WDAError(status=27, value={})']), ('倒计时关闭', ["name=结束执行click操作失败，失败原因==HTTPConnectionPool(host='localhost', port=8300): Read timed out. (read timeout=120)", "处理alert操作失败，失败原因==HTTPConnectionPool(host='localhost', port=8300): Max retries exceeded with url: /session/C355E327-9A9D-46DD-9025-88B7122CF02F/alert/accept (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a3a0048>: Failed to establish a new connection: [Errno 60] Operation timed out'))"])], 'fail': [], 'skip': [('选择题开启', '执行次数为0，跳过'), ('选择题关闭', '执行次数为0，跳过'), ('懂不懂开启', '执行次数为0，跳过'), ('懂不懂关闭', '执行次数为0，跳过'), ('判断题开启', '执行次数为0，跳过'), ('判断题关闭', '执行次数为0，跳过'), ('做题开启', '执行次数为0，跳过'), ('轻选择题开启', '执行次数为0，跳过'), ('发积分开启', '执行次数为0，跳过'), ('点名开启', '执行次数为0，跳过'), ('点名关闭', '执行次数为0，跳过'), ('倒计时开启', '执行次数为0，跳过'), ('课件休息', '执行次数为0，跳过'), ('课件休息关闭', '执行次数为0，跳过'), ('虚拟互动', '执行次数为0，跳过'), ('登出', '执行次数为0，跳过')]}
    case=["tutor"]
    answer={"tutor":0}
    res = result(time,fp,title="UI自动化测试报告",tutor=tutor)
    # result()
    res.generatereport()
    # print (res.chart())
    # res.generaterdetail("zuoti")
    # print(len(tutor.get("success")))


