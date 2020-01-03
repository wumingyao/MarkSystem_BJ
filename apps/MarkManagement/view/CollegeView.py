#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_College table.

Here are operations:
get_college_list: GET    http://localhost:8000/api/v1/college/display
           query: GET    http://localhost:8000/api/v1/college/format
          insert: POST   http://localhost:8000/api/v1/college/format
          update: PUT    http://localhost:8000/api/v1/college/format
          remove: DELETE http://localhost:8000/api/v1/college/format
"""
from apps.MarkManagement.view.common import *


class CollegeViewSet(viewsets.ViewSet):

    def get_college_list(self, request):
        """
        Get t_College join t_University table list
        :param request: the request from browser. 用来获取access_token和查询条件
        :return: JSON response. 包括code, message, subjects(opt), count(opt)
                1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                2、如果所有参数为空，即Params中没有内容，返回parameter_missed的JSON response
                3、如果符合条件，尝试查询
                    查询失败，返回query_failed的JSON response
                    查询成功，返回JSON response包括code, message, subjects, count，状态码2000

        """
        access_token = request.META.get("HTTP_TOKEN")

        if not token_verify(access_token):
            return token_invalid()

        id = request.GET.get('id')
        name = request.GET.get('name')
        university_id = request.GET.get('university_id')

        if id is None and name is None and university_id is None:
            return parameter_missed()

        college_set = College.objects.all()
        if university_id is None:
            if id is not None:
                college_set = college_set.filter(id=id)
            if name is not None:
                college_set = college_set.filter(name__contains=name)
        else:
            college_set = college_set.filter(university_id=university_id)

        # 对象取字典
        # college_set = college_set.values()
        result = []
        for college in college_set:
            collegeDict = model_to_dict(college)

            # 将College对象中的'university'属性名字改为'university_id'
            collegeDict['university_id'] = collegeDict['university']
            del collegeDict['university']

            # 因为外键关系 通过点语法可以直接取到另一张表对应的对象 并将另一张表内的信息命名为'university_message'
            collegeDict['university_message'] = model_to_dict(college.university)
            result.append(collegeDict)

        if len(result) == 0:
            return parameter_missed()

        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result,
            'count': len(result),
        }

        return JsonResponse(result, safe=False)

    def query(self, request):
        """
        Query t_College table
        :param request: the request from browser. 用来获取access_token和查询条件
        :return: JSON response. 包括code, message, subjects(opt), count(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果所有参数为空，即Params中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试查询
                    查询失败，返回query_failed的JSON response
                    查询成功，返回JSON response包括code, message, subjects, count，状态码2000
        """
        access_token = request.META.get("HTTP_TOKEN")

        if not token_verify(access_token):
            return token_invalid()

        id = request.GET.get('id')
        name = request.GET.get('name')
        university_id = request.GET.get('university_id')

        if id is None and name is None and university_id is None:
            return parameter_missed()

        college_set = College.objects.all()
        if university_id is None:
            if id is not None:
                college_set = college_set.filter(id=id)
            if name is not None:
                college_set = college_set.filter(name__contains=name)
        else:
            college_set = college_set.filter(university_id=university_id)

        # 对象取字典
        college_set = college_set.values()
        result = []

        for college in college_set:
            result.append(college)

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
        Insert data into t_College table
        :param request: the request from browser. 用来获取access_token和插入参数
        :return: JSON response. 包括code, message, subjects(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试插入
                    插入失败，返回insert_failed的JSON response
                    插入成功，返回JSON response包括code, message, subjects，状态码2001
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
            university_id = subjectDict.get('university_id')

            if name is None or university_id is None:
                continue

            college = College()
            if name:
                college.name = name
            if shortname:
                college.shortname = shortname
            if university_id:
                university_set = University.objects.filter(id=university_id)
                if university_set.count() == 0:
                    continue
                college.university = university_set[0]

            try:
                college.save()
            except Exception as e:
                continue
            else:
                ids.append({'id': college.id})
                tag = True

        if tag:
            return JsonResponse({'subjects': ids, 'code': '2001', 'message': status_code['2001']}, safe=False)
        else:
            return insert_failed()

    def update(self, request):
        """
        Update t_College table
        :param request: the request from browser. 用来获取access_token和更新条件
        :return: JSON response. 包括code, message, subjects(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试更新
                    更新失败，返回update_failed的JSON response
                    更新成功，返回JSON reponse包括code, message, subjects，状态码2005
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
            university_id = subjectDict.get('university_id')

            college_set = College.objects.filter(id=id)

            for college in college_set:
                if name:
                    college.name = name
                if shortname:
                    college.shortname = shortname

                # 如果修改信息包括university_id 则需要修改college外键university指向的对象
                if university_id:
                    university_set = University.objects.filter(id=university_id)
                    if not university_set.exists():
                        continue
                    college.university = university_set[0]
                try:
                    college.save()
                except Exception as e:
                    continue
                else:
                    ids.append({'id': college.id})
                    tag = True

        if tag:
            return JsonResponse({'subjects': ids, 'code': '2005', 'message': status_code['2005']}, safe=False)
        else:
            return update_failed()

    def remove(self, request):
        """
        Remove data from t_College table
        :param request: the request from browser. 用来获取access_token和删除条件
        :return: JSON response. 包括code, message
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试删除
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

            college_set = College.objects.filter(id=id)
            if not college_set.exists():
                continue

            try:
                college_set.delete()
            except Exception as e:
                continue
            else:
                tag = True

        if tag:
            return delete_succeed()
        else:
            return delete_failed()
