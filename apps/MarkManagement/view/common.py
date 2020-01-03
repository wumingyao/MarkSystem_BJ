#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_Token table.
This file also stores the status codes which are used to pass information between Server and Browser.
Token is used to forbid illegal operations, such as input url to delete the data of Server.

Here are operations:
           create_md5(pwd): 获取原始密码+salt的md5值
token_verify(access_token): 验证token
           token_invalid(): "code": 4011, "message": 'Error, Bad token'                 or '错误，无效的token'
    manager_check_failed(): "code": 4027, "message": 'Error, No authorized permissions' or '错误，权限认证不通过'
        parameter_missed(): "code": 4023, "message": 'Error, Missing parameters'        or '错误，参数缺失'
           query_succeed(): "code": 2000, "message": 'OK, with Response'                or '成功，服务器已响应'
            query_failed(): "code": 4036, "message": 'Error, No Matching Query Data'    or '错误，没有符合查询的数据'
          insert_succeed(): "code": 2001, "message": 'OK, Add new resource'             or '成功，服务器添加新资源'
           insert_failed(): "code": 4037, "message": 'Error, Data Insert Failed'        or '错误，数据插入失败'
          update_succeed(): "code": 2005, "message": 'OK, And need to Refresh'          or '成功，资源需要被刷新'
           update_failed(): "code": 4038, "message": 'Error, Data Update Failed'        or '错误，数据更新失败'
          delete_succeed(): "code": 2004, "message": 'OK, No Response content'          or '成功，无响应内容'
           delete_failed(): "code": 4039, "message": 'Error, Data Delete Failed'        or '错误，数据删除失败'

warning: 解析json、插入新值、更新新值、删除值时使用try
warning: post, put, delete接受值用request.data
"""

# system
from rest_framework import viewsets
from django.db.models import Q
from django.http import JsonResponse
from random import Random
from hashlib import md5
# custom
from apps.MarkManagement.model.models import *
from apps.MarkManagement.model.view_models import *
from django.forms.models import model_to_dict
from MarkSystem.settings import DEBUG

# 自定义状态码
status_code = {}
if DEBUG:

    status_code = {
        # 2--- 表示成功

        '2000': 'OK, with Response',
        '2001': 'OK, Add new resource',
        '2002': 'OK, Request accepted',
        '2004': 'OK, No Response content',
        '2005': 'OK, And need to Refresh',
        '2019': 'OK，partial resources insert failed',

        # 4--- 表示失败
        # -01- 表示用户 token 认证失败
        '4010': 'Error, Require token',
        '4011': 'Error, Bad token',
        '4012': 'Error, Token out of date',
        '4014': 'Error, Forbidden token',
        '4018': 'Error, Too much connections',

        # -02- 表示用户身份认证失败
        '4020': 'Error, User is not exist',
        '4021': 'Error, Username or password is incorrect',
        '4022': 'Error, User out of date',
        '4023': 'Error, User already exists',
        '4024': 'Error, Forbidden user',
        '4027': 'Error, No authorized permissions',

        # -03- 表示请求本身错误
        '4030': 'Error, No match API',
        '4031': 'Error, No match Request Type',
        '4032': 'Error, Missing parameters',
        '4033': 'Error, Not Allowed',
        '4035': 'Error, Gone',
        '4036': 'Error, No Matching Query Data',
        '4037': 'Error, Data Insert Failed',
        '4038': 'Error, Data Update Failed',
        '4039': 'Error, Data Delete Failed',
        '40329': 'Error, Too Many Requests',

        # 5--- 表示服务器失败
        '5001': 'Server is outline',
        '5003': 'Can not access database',
        '5004': 'Gateway Forbidden',
        '5101': 'Server is updating',
        '5201': 'Service Stopped'
    }
else:

    status_code = {
        # 2--- 表示成功

        '2000': '成功，服务器已响应',
        '2001': '成功，服务器添加新资源',
        '2002': '成功，请求被接收',
        '2004': '成功，无响应内容',
        '2005': '成功，资源需要被刷新',
        '2019': '成功，部分资源插入失败',
        # 4--- 表示失败
        # -01- 表示用户 token 认证失败
        '4010': '错误，需要token验证',
        '4011': '错误，无效的token',
        '4012': '错误，过期的token',
        '4014': '错误，被禁止的token',
        '4018': '错误，连接次数过多',

        # -02- 表示用户身份认证失败
        '4020': '错误，用户不存在',
        '4021': '错误，用户名或密码错误',
        '4022': '错误，用户登录已过期',
        '4023': '错误，注册用户已存在',
        '4024': '错误，用户被禁止访问',
        '4027': '错误，权限认证不通过',

        # -03- 表示请求本身错误
        '4030': '错误，没有符合的API',
        '4031': '错误，没有符合的请求类型',
        '4032': '错误，参数缺失',
        '4033': '错误，请求被拒绝',
        '4035': '错误，已走远',
        '4036': '错误，没有符合查询的数据',
        '4037': '错误，数据插入失败',
        '4038': '错误，数据更新失败',
        '4039': '错误，数据删除失败',
        '40329': '错误，请求次数过多',

        # 5--- 表示服务器失败
        '5001': '服务器已离线',
        '5003': '无法连接数据库',
        '5004': '网关禁止',
        '5101': '服务器更新中',
        '5201': '服务已停止'
    }
# # 课程状态
# lessonStatus = {
#     0: 'running',
#     1: 'certificate',
#     2: 'preparation',
#     3: 'parsed',
#     4: 'archived',
#     5: 'dropped'
# }
# # 课程类型
# lessonType = {
#     0: '基础必修',
#     1: '专业必修',
#     2: '基础选修',
#     3: '专业选修',
#     4: '辅修',
#     5: '特殊'
# }
# # 分数类型
# pointType = {
#     0: '出席',
#     1: '作业',
#     2: '课时表现',
#     3: '额外加分',
#     4: '期中考试',
#     5: '期末考试'
# }

current_semester = "2019年春季"


def create_md5(pwd):
    """
    获取原始密码 + salt的md5值
    MD5的全称是Message-Digest Algorithm 5（信息-摘要算法），128位长度，目前MD5是一种不可逆算法。
    hexdigest()目的是为了发现原始数据是否被人篡改过，因为摘要函数是一个单向函数，计算f(data)很容易，但通过digest反推data却非常困难。
    :param pwd: 原始密码
    :return:
    """
    salt = ''
    length = 10
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    random = Random()
    for _ in range(length):
        # 每次从chars中随机取一位
        salt += chars[random.randint(0, len(chars) - 1)]
    md5_obj = md5()
    data = pwd + salt
    md5_obj.update(data.encode(encoding='utf8'))
    return md5_obj.hexdigest()


#
def token_verify(access_token):
    """
    验证token
    :param access_token: 获取到的token
    :return: token是否有效
    """
    if access_token is None:
        return False
    # 在数据库中查找token是否存在
    access_token_set = Token.objects.filter(token_text=access_token)
    if not access_token_set.exists():
        return False
    return True


def token_invalid():
    """
    'Error, Bad token' or '错误，无效的token'
    :return: JSON response，携带无效token对应的状态码以及对应状态信息
    """
    return JsonResponse({'code': '4011', 'message': status_code['4011']})


def manager_check_failed():
    """
    'Error, No authorized permissions' or '错误，权限认证不通过'
    :return: JSON response，携带越权操作的状态码以及对应状态信息
    """
    return JsonResponse({'code': '4027', 'message': status_code['4027']}, safe=False)


def parameter_missed():
    """
    'Error, Missing parameters' or '错误，参数缺失'
    :return: JSON response，携带参数缺失的状态码以及对应状态信息
    """
    return JsonResponse({'code': '4032', 'message': status_code['4032']}, safe=False)


def query_succeed():
    """
    'OK, with Response' or '成功，服务器已响应'
    :return: JSON response，携带查询成功的状态码以及对应状态信息
    """
    return JsonResponse({'code': '2000', 'message': status_code['2000']}, safe=False)


def query_failed():
    """
    'Error, No Matching Query Data' or '错误，没有符合查询的数据'
    :return: JSON response，携带查询失败的状态码以及对应状态信息
    """
    return JsonResponse({'code': '4036', 'message': status_code['4036']}, safe=False)


def insert_succeed():
    """
    'OK, Add new resource' or '成功，服务器添加新资源'
    :return: JSON response，携带插入成功的状态码以及对应状态信息
    """
    return JsonResponse({'code': '2001', 'message': status_code['2001']}, safe=False)


def insert_failed():
    """
    'Error, Data Insert Failed' or '错误，数据插入失败'
    :return: JSON response，携带数据插入失败的状态码以及对应状态信息
    """
    return JsonResponse({'code': '4037', 'message': status_code['4037']}, safe=False)


def update_succeed():
    """
    'OK, And need to Refresh' or '成功，资源需要被刷新'
    :return: JSON response，携带更新成功的状态码以及对应状态信息
    """
    return JsonResponse({'code': '2005', 'message': status_code['2005']}, safe=False)


def update_failed():
    """
    'Error, Data Update Failed' or '错误，数据更新失败'
    :return: JSON response，携带更新失败的状态码以及对应状态信息
    """
    return JsonResponse({'code': '4038', 'message': status_code['4038']}, safe=False)


def delete_succeed():
    """
    'OK, No Response content' or '成功，无响应内容'
    :return: JSON response，携带删除成功的状态码以及对应状态信息
    """
    return JsonResponse({'code': '2004', 'message': status_code['2004']}, safe=False)


def delete_failed():
    """
    'Error, Data Delete Failed' or '错误，数据删除失败'
    :return: JSON response，携带删除失败的状态码以及对应状态信息
    """
    return JsonResponse({'code': '4039', 'message': status_code['4039']}, safe=False)
