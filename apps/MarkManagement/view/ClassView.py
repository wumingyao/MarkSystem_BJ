#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_Class table.

Here are operations:
query_wrapper: GET    http://localhost:8000/api/v1/table/class_field/wrapper
        query: GET    http://localhost:8000/api/v1/table/class_field/format
       insert: POST   http://localhost:8000/api/v1/table/class_field/format
       remove: DELETE http://localhost:8000/api/v1/table/class_field/format
"""

from apps.MarkManagement.view.common import *


class ClassViewSet(viewsets.ViewSet):

    def query_wrapper(self, request):
        """
        根据筛选选项获取教学班拥有学生数及学生的id
        :param request: the request from browser. 用来获取access_token
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

        subjects = request.data.get('subjects')
        if subjects is None:
            return parameter_missed()

        result = []

        for subjectsDict in subjects:

            id = subjectsDict.get('id')
            # lesson_id = request.GET.get('lesson_id')
            student_id = subjectsDict.get('student_id')
            # sid = request.GET.get('sid')
            # sname = request.GET.get('sname')
            classInfo_id = subjectsDict.get('classInfo_id')

            if id is None and student_id is None and classInfo_id is None:
                continue

            class_set = Class.objects.all()
            if id is not None:
                class_set = class_set.filter(id=id)
            if student_id is not None:
                class_set = class_set.filter(student_id=student_id)
            if classInfo_id is not None:
                class_set = class_set.filter(classInfo_id=classInfo_id)
            class_set = class_set.values()

            for one_class in class_set:
                result.append(one_class)

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

    def query(self, request):
        """
        Query t_Class table
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
        # lesson_id = request.GET.get('lesson_id')
        student_id = request.GET.get('student_id')
        # sid = request.GET.get('sid')
        # sname = request.GET.get('sname')
        classInfo_id = request.GET.get('classInfo_id')

        if id is None and student_id is None and classInfo_id is None:
            return parameter_missed()

        class_set = Class.objects.all()
        if id is not None:
            class_set = class_set.filter(id=id)
        if student_id is not None:
            class_set = class_set.filter(student_id=student_id)
        if classInfo_id is not None:
            class_set = class_set.filter(classInfo_id=classInfo_id)

        class_set = class_set.values()
        result = []

        for one_class in class_set:
            result.append(one_class)

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
        Insert t_Class table
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

        for subjectsDict in subjects:
            # lesson_id = subjectsDict.get('lesson_id')
            student_id = subjectsDict.get('student_id')
            # sname = subjectsDict.get('sname')
            # sid = subjectsDict.get('sid')
            # index = subjectsDict.get('index')
            classInfo_id = subjectsDict.get('classInfo_id')

            if student_id is None or classInfo_id is None:
                continue

            new_class = Class()
            # if lesson_id:
            #    lesson_set = Lesson.objects.filter(id=lesson_id)
            #   if lesson_set.exists() == False:
            #      continue
            # new_class.lesson = lesson_set[0]
            if student_id:
                student_set = Student.objects.filter(id=student_id)
                if not student_set.exists():
                    continue
                new_class.student = student_set[0]

            if classInfo_id:
                classInfo_set = ClassInfo.objects.filter(id=classInfo_id)
                if not classInfo_set.exists():
                    continue
                new_class.classInfo = classInfo_set[0]

            try:
                new_class.save()
                ids.append({'id': new_class.id})
                tag = True
            except Exception as e:
                continue

        if tag:
            return JsonResponse(
                {'subjects': ids,
                 'code': '2001',
                 'message': status_code['2001']}, safe=False)
        else:
            return insert_succeed()

    def remove(self, request):
        """
        Remove t_Class table
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

            class_set = Class.objects.filter(id=id)
            if not class_set.exists():
                continue

            try:
                class_set.delete()
                tag = True
            except Exception as e:
                continue

        if tag:
            return delete_succeed()
        else:
            return delete_failed()
