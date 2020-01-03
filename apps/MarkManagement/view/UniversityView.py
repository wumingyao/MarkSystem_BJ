#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_University table.

Here are operations:
 query: GET    http://localhost:8000/api/v1/university/format
insert: POST   http://localhost:8000/api/v1/university/format
update: PUT    http://localhost:8000/api/v1/university/format
remove: DELETE http://localhost:8000/api/v1/university/format
"""

from apps.MarkManagement.view.common import *


class UniversityViewSet(viewsets.ViewSet):

    def query(self, request):
        """
        Query t_University table
        :param request: the request from browser. 用来获取access_token和查询条件
        :return: JSON response. 包括code, message, subjects(opt), count(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果所有参数为空，即Params中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试查询
                    查询失败，返回query_failed的JSON response
                    查询成功，返回JSON response包括code, message, subjects, count，状态码2000
        """
        # 获取token
        access_token = request.META.get("HTTP_TOKEN")

        # 验证token
        if not token_verify(access_token):
            return token_invalid()

        id = request.GET.get('id')
        name = request.GET.get('name')
        shortname = request.GET.get('shortname')

        # 处理所有参数为空的情况
        if id is None and name is None and shortname is None:
            return parameter_missed()

        university_set = University.objects.all()

        # 根据参数过滤
        if id is not None:
            university_set = university_set.filter(id=id)
        if name is not None:
            university_set = university_set.filter(name=name)
        if shortname:
            university_set = university_set.filter(shortname=shortname)

        # 对象取字典数组
        university_set = university_set.values()

        # 结果集
        result = []

        # 遍历数组字典
        for university in university_set:
            result.append(university)

        # 处理过滤结果为空的情况
        if len(result) == 0:
            return query_failed()

        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result,
            'count': len(result),
        }

        # 返回查询结果
        return JsonResponse(result, safe=False)

    def insert(self, request):
        """
        Insert data into t_University table
        :param request: the request from browser. 用来获取access_token和插入参数
        :return: JSON response. 包括code, message, subjects(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试插入
                    插入失败，返回insert_failed的JSON response
                    插入成功，返回JSON response包括code, message, subjects，状态码2001
        """
        # 获取并验证token
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        # 解析JSON请求体
        post_data = request.data
        subjects = post_data.get('subjects')

        # 处理subjects为空的情况
        if subjects is None:
            return parameter_missed()

        # 请求标记
        tag = False
        ids = []

        # 遍历请求体数组参数
        for subjectDict in subjects:
            name = subjectDict.get('name')
            shortname = subjectDict.get('shortname')

            if name is None:
                continue

            # 将请求体内数据封装为一个新对象
            university = University()
            if name:
                university.name = name
            if shortname:
                university.shortname = shortname

            # 将对象保存到表内
            try:
                university.save()
                ids.append({'id': university.id})
                tag = True
            except Exception as e:
                continue

        # 根据插入操作的成功与失败，返回对应JSON response
        if tag:
            return JsonResponse({'subjects': ids, 'code': '2001', 'message': status_code['2001']}, safe=False)
        else:
            return insert_failed()

    def update(self, request):
        """
        Update t_University table
        :param request: the request from browser. 用来获取access_token和更新条件
        :return: JSON response. 包括code, message, subjects(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试更新
                    更新失败，返回update_failed的JSON response
                    更新成功，返回JSON reponse包括code, message, subjects，状态码2005
        """
        # 获取并验证token
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        # 解析JSON请求体
        put_data = request.data
        subjects = put_data.get('subjects')

        # 如果subjects为空，返回对应JSON response
        if subjects is None:
            return parameter_missed()

        # 请求标记
        tag = False
        ids = []

        # 遍历请求体数组参数
        for subjectDict in subjects:
            id = subjectDict.get('id')
            name = subjectDict.get('name')
            shortname = subjectDict.get('shortname')

            # 过滤到需要修改的对象
            university_set = University.objects.filter(id=id)

            # 更新其信息
            for university in university_set:
                if name:
                    university.name = name
                if shortname:
                    university.shortname = shortname

                # 保存至表内
                try:
                    university.save()
                except Exception as e:
                    continue
                else:
                    ids.append({'id': university.id})
                    tag = True

        # 根据更新操作的成功与失败，返回对应JSON response
        if tag:
            return JsonResponse({'subjects': ids, 'code': '2005', 'message': status_code['2005']}, safe=False)
        else:
            return update_failed()

    def remove(self, request):
        """
        Remove data from t_University table
        :param request: the request from browser. 用来获取access_token和删除条件
        :return: JSON response. 包括code, message
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试删除
                    删除失败，返回delete_failed的JSON response
                    删除成功，返回delete_succeed的JSON response
        """
        # 获取并验证token
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        # 解析JSON请求体
        delete_data = request.data
        subjects = delete_data.get('subjects')

        # 处理subjects为空的情况
        if subjects is None:
            return parameter_missed()

        tag = False

        # 遍历请求体数组参数
        for subjectDict in subjects:
            id = subjectDict.get('id')
            if id is None:
                continue

            university_set = University.objects.filter(id=id)
            if not university_set.exists():
                continue

            # 删除对应数据
            try:
                university_set.delete()
            except Exception as e:
                continue
            else:
                tag = True

        # 根据删除操作的成功与失败，返回对应JSON response
        if tag:
            return delete_succeed()
        else:
            return delete_failed()
