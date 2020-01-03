#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_Student table.

Here are operations:
get_student_list: GET    http://localhost:8000/api/v1/student/display
           query: GET    http://localhost:8000/api/v1/student/format
          insert: POST   http://localhost:8000/api/v1/student/format
          update: PUT    http://localhost:8000/api/v1/student/format
          remove: DELETE http://localhost:8000/api/v1/student/format
"""

from apps.MarkManagement.view.common import *


class StudentViewSet(viewsets.ViewSet):

    def get_student_match(self, request):
        """
        根据学号和专业进行模糊匹配
        Get t_Student table list
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

        sid_str = request.GET.get('sid')
        majorName_str = request.GET.get('majorName')

        result = []

        # 如果学号和专业都为空
        if sid_str is None and majorName_str is None:
            return parameter_missed()
        # 如果学号为空，根据专业模糊匹配
        elif sid_str is None:
            student_set = Student.objects.filter(majorName__contains=majorName_str).values('id', 'sid', 'name',
                                                                                           'majorName', 'collegeName',
                                                                                           'year')
            result = list(student_set)
        # 如果专业为空，根据学号模糊匹配
        elif majorName_str is None:
            student_set = Student.objects.filter(sid__contains=sid_str).values('id', 'sid', 'name',
                                                                               'majorName', 'collegeName',
                                                                               'year')
            result = list(student_set)
        # 如果两个都有，根据专业和学号进行模糊匹配
        else:
            student_set = Student.objects.filter(
                Q(sid__contains=sid_str) & Q(majorName__contains=majorName_str)).values('id', 'sid', 'name',
                                                                                        'majorName', 'collegeName',
                                                                                        'year')
            result = list(student_set)
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

    def get_student_list(self, request):
        """
        Get t_Student table list
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
        sid = request.GET.get('sid')
        name = request.GET.get('name')
        major_id = request.GET.get('major_id')
        year = request.GET.get('year')
        classInfo_id = request.GET.get('classInfo_id')
        college_id = request.GET.get('college_id')
        # 新增字段
        majorName = request.GET.get('majorName')
        collegeName = request.GET.get('collegeName')

        result = []

        if classInfo_id is not None:
            student_set = Student.objects.filter(class__classInfo_id=classInfo_id)

            for student in student_set:
                student_dict = model_to_dict(student)
                student_dict['major_id'] = student_dict['major']
                del student_dict['major']

                major_dict = model_to_dict(student.major)
                major_dict['college_id'] = major_dict['college']
                del major_dict['college']

                student_dict['major_message'] = major_dict

                college_dict = model_to_dict(student.major.college)
                college_dict['university_id'] = college_dict['university']
                del college_dict['university']
                student_dict['college_message'] = college_dict

                result.append(student_dict)
        else:
            if id is None and sid is None and major_id is None and year is None and name is None and college_id is None and collegeName is None and majorName is None:
                return parameter_missed()

            student_set = Student.objects.all()
            if id is not None:
                student_set = student_set.filter(id=id)
            if sid is not None:
                student_set = student_set.filter(sid=sid)
            if name is not None:
                student_set = student_set.filter(name=name)
            if major_id is not None:
                student_set = student_set.filter(major_id=major_id)
            if year is not None:
                student_set = student_set.filter(year=year)
            if majorName is not None:
                student_set = student_set.filter(majorName=majorName)
            if collegeName is not None:
                student_set = student_set.filter(collegeName=collegeName)
            if college_id:
                student_set = student_set.filter(major__college__id=college_id)

            for student in student_set:
                student_dict = model_to_dict(student)
                student_dict['major_id'] = student_dict['major']
                del student_dict['major']

                major_dict = model_to_dict(student.major)
                major_dict['college_id'] = major_dict['college']
                del major_dict['college']
                student_dict['major_message'] = major_dict

                college_dict = model_to_dict(student.major.college)
                college_dict['university_id'] = college_dict['university']
                del college_dict['university']
                student_dict['college_message'] = college_dict

                result.append(student_dict)

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
        Query t_Student table
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
        sid = request.GET.get('sid')
        name = request.GET.get('name')
        major_id = request.GET.get('major_id')
        year = request.GET.get('year')
        # 新增字段
        majorName = request.GET.get('majorName')
        collegeName = request.GET.get('collegeName')
        classInfo_id = request.GET.get('classInfo_id')
        college_id = request.GET.get('college_id')

        result = []

        if classInfo_id is not None:
            student_set = Student.objects.filter(class__classInfo_id=classInfo_id)
            student_set = student_set.values()
            for student in student_set:
                result.append(student)
        else:
            if id is None and sid is None and major_id is None \
                    and year is None and name is None and college_id is None and majorName is None and collegeName is None:
                return parameter_missed()

            student_set = Student.objects.all()
            if id is not None:
                student_set = student_set.filter(id=id)
            if sid is not None:
                student_set = student_set.filter(sid=sid)
            if name is not None:
                student_set = student_set.filter(name=name)
            if major_id is not None:
                student_set = student_set.filter(major_id=major_id)
            if year is not None:
                student_set = student_set.filter(year=year)
            if majorName is not None:
                student_set = student_set.filter(majorName=majorName)
            if collegeName is not None:
                student_set = student_set.filter(collegeName=collegeName)
            if college_id:
                student_set = student_set.filter(major__college__id=college_id)
            student_set = student_set.values()

            for student in student_set:
                result.append(student)

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
        Insert t_Student table
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
        succeed_ids = []
        failed_sids = []
        repeated_ids = []

        for subjectDict in subjects:

            sid = subjectDict.get('sid')
            name = subjectDict.get('name')
            major_id = subjectDict.get('major_id')
            year = subjectDict.get('year')
            # 新增字段
            majorName = subjectDict.get('majorName')
            collegeName = subjectDict.get('collegeName')

            # 修改_吴
            # 增加班级编号，把学生和班级关联在一起
            classInfo_id = subjectDict.get('classInfo_id')

            if sid is None or name is None or major_id is None:
                continue

            student = Student()
            new_class = Class()
            if sid is not None:
                student_set = Student.objects.filter(sid=sid)

                if student_set.exists():
                    repeated_ids.append({"id": student_set[0].id})
                    continue

                student.sid = sid

            if name is not None:
                student.name = name
            if major_id is not None:
                student.major_id = major_id
            if year is not None:
                student.year = year
            if majorName is not None:
                student.majorName = majorName
            if collegeName is not None:
                student.collegeName = collegeName
            try:
                student.save()
                student_set = Student.objects.filter(sid=sid)
                new_class.student = student_set[0]

                if classInfo_id is not None:
                    classInfo_set = ClassInfo.objects.filter(id=classInfo_id)
                    new_class.classInfo = classInfo_set[0]
                    new_class.save()
                succeed_ids.append({'id': student.id})
                tag = True
            # except IntegrityError:
            #     print("exist")
            except Exception:
                failed_sids.append({"sid": sid})

        subjects = {
            "succeed_ids": succeed_ids,
            "failed_sids": failed_sids,
            "repeated_ids": repeated_ids
        }
        if tag:
            return JsonResponse(
                {'subjects': subjects,
                 'code': '2001',
                 'message': status_code['2001']}, safe=False)
        else:
            return JsonResponse(
                {'subjects': subjects,
                 'code': '4037',
                 'message': status_code['4037']}, safe=False)

    def update(self, request):
        """
        Update t_Student table
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
            sid = subjectDict.get('sid')
            major_id = subjectDict.get('major_id')
            year = subjectDict.get('year')
            # 新增字段
            majorName = subjectDict.get('majorName')
            collegeName = subjectDict.get('collegeName')
            student_set = Student.objects.filter(id=id)

            for student in student_set:
                if name:
                    student.name = name
                if sid:
                    student.sid = sid
                if major_id:
                    student.major_id = major_id
                if year:
                    student.year = year
                if majorName:
                    student.majorName = majorName
                if collegeName:
                    student.collegeName = collegeName
                try:
                    student.save()
                    ids.append({'id': student.id})
                    tag = True
                except Exception as e:
                    continue

        if tag:
            return JsonResponse(
                {'subjects': ids,
                 'code': '2005',
                 'message': status_code['2005']}, safe=False)
        else:
            return update_failed()

    def remove(self, request):
        """
        Remove t_Student table
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

            student_set = Student.objects.filter(id=id)

            if not student_set.exists():
                continue

            try:
                student_set.delete()
                tag = True
            except Exception as e:
                continue

        if tag:
            return delete_succeed()
        else:
            return delete_failed()
