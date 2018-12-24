import os
def is_testcase(data):
    if not isinstance(data,dict):
        return False
    if 'testcases' not in data:
        return False
    if not isinstance(data['testcases'],list):
        return False
    return True

def is_testcase_path(path):
    if not isinstance(path,str):
        return False
    else:
        if not os.path.exists(path):
            return False
        else:
            if not path.endswith(('json','xlsx')):
                return False
    return True


def check(value1,operation,value2):
    if operation in ['==','equal','eq']:
        return value1==value2
    if operation in ['!=','ne','neq']:
        return value1!=value2
    if operation in ['>','gt']:
        return value1 > value2
    if operation in ['<','lt']:
        return value1 < value2
    if operation in ['>=','gte','ge']:
        return value1 >=value2
    if operation in ['<=','lte','le']:
        return value1 <=value2
    if operation in ['not']:
        return not value1
    if operation in ['notin','ni']:
        return value1 not in value2
    if operation in ['in']:
        return value1 in value2
