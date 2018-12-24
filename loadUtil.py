import xlrd
import os
import json
def load_file(path):
    if not os.path.isfile(path):
        raise "{}文件不存在".format(path)
    file_end=os.path.splitext(path)[1].lower()
    if file_end=='.json':
        return load_json_file(path)
    elif file_end=='.xlxs':
        return load_excel_file(path)
    else:
        print('文件格式不支持，{}'.format(path))
def load_json_file(path):
    lines=[]
    with open(path,encoding='utf-8') as f:
        for line in f.readlines():
            lines.append(line)
    try:
        content=json.loads('\n'.join(lines))
    except Exception as e:
        raise e
    return content

def load_excel_file(path):
    workbooks=xlrd.open_workbook(path)
    config_sheet=workbooks.sheet_by_index(0)
    testcases_sheet=workbooks.sheet_by_index(1)
    data={}
    _config={}
    for i in range(config_sheet.nrows):
        conf=config_sheet.row_values(i)
        _config[conf[0]]=conf[1]
    data['config']=_config

    testcases=[]
    header=testcases_sheet.row_values(0)
    for i in range(1,testcases_sheet.nrows):
        _testcase={}
        rows=testcases_sheet.row_values(i)
        for j in range(testcases_sheet.ncols):
            _testcase[header[j]]=rows[j]
        testcases.append(_testcase)

    data['cases']=testcases
