#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_Major table.

Here are operations:
 query: GET    http://localhost:8000/api/v1/major/format
insert: POST   http://localhost:8000/api/v1/major/format
update: PUT    http://localhost:8000/api/v1/major/format
remove: DELETE http://localhost:8000/api/v1/major/format
"""

from apps.MarkManagement.view.common import *


class MajorViewSet(viewsets.ViewSet):

    def query(self, request):
        """
        Query t_Major table
        :param request: the request from browser. 用来获取access_token和查询条件
        :return: JSON response. 包括code, message, subjects(opt), count(opt)
                1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                2、如果所有参数为空，即Params中没有内容，返回parameter_missed的JSON response
                3、如果符合条件，尝试查询
                    查询失败，返回query_failed的JSON response
                    查询成功，subjects会包括查询数据的信息，状态码2000
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        id = request.GET.get('id')
        name = request.GET.get('name')
        college_id = request.GET.get('college_id')

        if id is None and name is None and college_id is None:
            return parameter_missed()

        major_set = Major.objects.all()
        if id:
            major_set = major_set.filter(id=id)
        if name:
            major_set = major_set.filter(name=name)
        if college_id:
            major_set = major_set.filter(college_id=college_id)

        result = []

        # 对象取字典
        major_set = major_set.values()
        for major in major_set:
            result.append(major)

        if len(result) == 0:
            return query_failed()

        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result,
            'count': len(result),
        }

        return JsonResponse(result, safe=False)

    def insert(self, request):
        """
        Insert data into t_Major table
        :param request: the request from browser. 用来获取access_token和插入参数
        :return: JSON response. 包括code, message, subjects(opt)
                1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                3、如果符合插入条件，尝试插入
                    插入失败，返回insert_failed的JSON response
                    插入成功，subjects会包括插入数据的信息，状态码2001
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        post_data = request.data
        subjects = post_data.get('subjects')

        if subjects is None:
            return parameter_missed()

        tag = False
        ids = []

        for subjectDict in subjects:
            name = subjectDict.get('name')
            shortname = subjectDict.get('shortname')
            college_id = subjectDict.get('college_id')

            if name is None or college_id is None:
                continue

            major = Major()
            if name:
                major.name = name
            if shortname:
                major.shortname = shortname

            if college_id:
                college_set = College.objects.filter(id=college_id)

                if not college_set.exists():
                    continue

                major.college = college_set[0]

            try:
                major.save()
            except Exception as e:
                continue
            else:
                ids.append({'id': major.id})
                tag = True

        if tag:
            return JsonResponse({'subjects': ids, 'code': '2001', 'message': status_code['2001']}, safe=False)
        else:
            return insert_failed()

    def update(self, request):
        """
        Update t_Major table
        :param request: the request from browser. 用来获取access_token和更新条件
        :return: JSON response. 包括code, message, subjects(opt)
                1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                3、如果符合更新条件，尝试更新
                    更新失败，返回update_failed的JSON response
                    更新成功，subjects会包括更新数据的信息，状态码2005
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        put_data = request.data
        subjects = put_data.get('subjects')
        if subjects is None:
            return parameter_missed()

        tag = False
        ids = []

        for subjectDict in subjects:
            id = subjectDict.get('id')
            name = subjectDict.get('name')
            shortname = subjectDict.get('shortname')
            college_id = subjectDict.get('college_id')

            major_set = Major.objects.filter(id=id)
            for major in major_set:
                if name:
                    major.name = name
                if shortname:
                    major.shortname = shortname

                if college_id:
                    college_set = College.objects.filter(id=college_id)
                    if not college_set.exists():
                        continue
                    major.college = college_set[0]
                major.save()

                try:
                    major.save()
                except Exception as e:
                    continue
                else:
                    ids.append({'id': major.id})
                    tag = True

        if tag:
            return JsonResponse({'subjects': ids, 'code': '2005', 'message': status_code['2005']}, safe=False)
        else:
            return update_failed()

    def remove(self, request):
        """
        Remove t_Major table
        :param request: the request from browser. 用来获取access_token和删除条件
        :return: JSON response. 包括code, message
                1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                3、如果符合更新条件，尝试删除
                    删除失败，返回delete_failed的JSON response
                    删除成功，返回delete_succeed的JSON response
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        delete_data = request.data
        subjects = delete_data.get('subjects')
        if subjects is None:
            return parameter_missed()

        tag = False

        for subjectDict in subjects:
            id = subjectDict.get('id')
            if id is None:
                continue

            Major.objects.filter(id=id).delete()
            major_set = Major.objects.filter(id=id)
            if not major_set.exists():
                continue

            try:
                major_set.delete()
            except Exception as e:
                continue
            else:
                tag = True

        if tag:
            return delete_succeed()
        else:
            return delete_succeed()
