#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_ClassInfo table.

Here are operations:
get_classInfo_full_message_all: GET    http://localhost:8000/api/v1/table/class_info/detail/all
    get_classInfo_full_message: GET    http://localhost:8000/api/v1/table/class_info/detail/some
                         query: GET    http://localhost:8000/api/v1/table/class_info/format
                        insert: POST   http://localhost:8000/api/v1/table/class_info/format
                        update: PUT    http://localhost:8000/api/v1/table/class_info/format
                        remove: DELETE http://localhost:8000/api/v1/table/class_info/format
"""
from apps.MarkManagement.view.common import *

import datetime


class ClassInfoViewSet(viewsets.ViewSet):

    def get_classInfo_full_message_all(self, request):
        """
        管理员获取符合参数条件的已有课程信息
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

        teacher_set = Teacher.objects.filter(token__token_text=access_token)
        teacher = teacher_set[0]
        if not teacher.is_manager:
            return manager_check_failed()

        result = []

        classInfo_set = ClassInfo.objects.all()
        for classInfo in classInfo_set:
            classInfo_dict = model_to_dict(classInfo)

            classInfo_dict['teacher_id'] = classInfo_dict['teacher']
            del classInfo_dict['teacher']
            teacher_dict = model_to_dict(classInfo.teacher)
            classInfo_dict['teacher_message'] = teacher_dict

            classInfo_dict['lesson_id'] = classInfo_dict['lesson']
            del classInfo_dict['lesson']
            lesson_dict = model_to_dict(classInfo.lesson)
            classInfo_dict['lesson_message'] = lesson_dict

            lesson_dict['college_id'] = lesson_dict['college']
            del lesson_dict['college']

            classInfo_dict['student_count'] = len(Student.objects.filter(class__classInfo__id=classInfo.id))

            # 识别当前学期
            semesterList = ['春季', '秋季', '夏季小学期', '秋季小学期', '其他']

            # 获取当前年月
            year = datetime.datetime.now().year

            month = datetime.datetime.now().month
            if month >= 3 and month <= 7:
                current_semester = str(year) + '年' + semesterList[0]
            elif month >= 9 and month <= 12:
                current_semester = str(year) + '年' + semesterList[1]
            elif month == 1:
                current_semester = str(year - 1) + '年' + semesterList[1]
            elif month == 8:
                current_semester = str(year) + '年' + semesterList[2]
            elif month == 2:
                current_semester = str(year) + '年' + semesterList[3]
            else:
                current_semester = str(year) + '年' + semesterList[4]

            classInfo_dict['current_semester'] = current_semester

            result.append(classInfo_dict)

        if len(result) == 0:
            return JsonResponse({
                'current_semester': current_semester,
                'code': '4036',
                'message': status_code['4036']},
                safe=False)

        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result,
            'count': len(result),
        }

        return JsonResponse(result, safe=False)

    def get_classInfo_full_message(self, request):
        """
        任课教师获取符合参数条件的已有课程信息
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
        # cid = request.GET.get('cid')
        cid = 'default'
        lesson_id = request.GET.get('lesson_id')
        teacher_id = request.GET.get('teacher_id')
        semester = request.GET.get('semester')
        week = request.GET.get('week')
        room = request.GET.get('room')

        if id is None and name is None and cid is None and teacher_id is None \
                and semester is None and week is None and room is None and lesson_id is None:
            return JsonResponse({"code": '4032', "message": status_code['4032']})

        # 此处待优化,all()
        classInfo_set = ClassInfo.objects.all()
        if id is not None:
            classInfo_set = classInfo_set.filter(id=id)
        if name is not None:
            classInfo_set = classInfo_set.filter(name__contains=name)
        if cid is not None:
            classInfo_set = classInfo_set.filter(cid=cid)
        if lesson_id is not None:
            classInfo_set = classInfo_set.filter(lesson_id=lesson_id)
        if teacher_id is not None:
            classInfo_set = classInfo_set.filter(teacher_id=teacher_id)
        if semester is not None:
            classInfo_set = classInfo_set.filter(semester__contains=semester)
        if week is not None:
            classInfo_set = classInfo_set.filter(week__contains=week)
        if room is not None:
            classInfo_set = classInfo_set.filter(room__contains=room)

        # 识别当前学期
        semesterList = ['春季', '秋季', '夏季小学期', '秋季小学期', '其他']

        # 获取当前年月
        year = datetime.datetime.now().year

        month = datetime.datetime.now().month
        if month >= 3 and month <= 7:
            current_semester = str(year) + '年' + semesterList[0]
        elif month >= 9 and month <= 12:
            current_semester = str(year) + '年' + semesterList[1]
        elif month == 1:
            current_semester = str(year - 1) + '年' + semesterList[1]
        elif month == 8:
            current_semester = str(year) + '年' + semesterList[2]
        elif month == 2:
            current_semester = str(year) + '年' + semesterList[3]
        else:
            current_semester = str(year) + '年' + semesterList[4]

        result = []
        for classInfo in classInfo_set:
            classInfo_dict = model_to_dict(classInfo)
            classInfo_dict['teacher_id'] = classInfo_dict['teacher']
            del classInfo_dict['teacher']
            if classInfo.teacher is None:
                teacher_dict = {}
            else:
                teacher_dict = model_to_dict(classInfo.teacher)

            classInfo_dict['lesson_id'] = classInfo_dict['lesson']
            del classInfo_dict['lesson']
            if classInfo.lesson is None:
                lesson_dict = {}
            else:
                lesson_dict = model_to_dict(classInfo.lesson)
                lesson_dict['college_id'] = lesson_dict['college']
                del lesson_dict['college']

            classInfo_dict['student_count'] = len(Student.objects.filter(class__classInfo__id=classInfo.id))
            classInfo_dict['lesson_message'] = lesson_dict
            classInfo_dict['teacher_message'] = teacher_dict
            classInfo_dict['current_semester'] = current_semester

            result.append(classInfo_dict)

        if len(result) == 0:
            return JsonResponse(
                {'current_semester': current_semester,
                 'code': '4036',
                 'message': status_code['4036']}, safe=False)

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
        获取符合参数条件的已有课程信息
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
        # cid = request.GET.get('cid')
        cid = 'default'
        teacher_id = request.GET.get('teacher_id')
        lesson_id = request.GET.get('lesson_id')
        semester = request.GET.get('semester')
        week = request.GET.get('week')
        room = request.GET.get('room')

        if id is None and name is None and cid is None and teacher_id is None \
                and semester is None and week is None and room is None and lesson_id is None:
            return JsonResponse({"code": '4032', "message": status_code['4032']})

        # 识别当前学期
        semesterList = ['春季', '秋季', '夏季小学期', '秋季小学期', '其他']

        # 获取当前年月
        year = datetime.datetime.now().year

        month = datetime.datetime.now().month
        if month >= 3 and month <= 7:
            current_semester = str(year) + '年' + semesterList[0]
        elif month >= 9 and month <= 12:
            current_semester = str(year) + '年' + semesterList[1]
        elif month == 1:
            current_semester = str(year - 1) + '年' + semesterList[1]
        elif month == 8:
            current_semester = str(year) + '年' + semesterList[2]
        elif month == 2:
            current_semester = str(year) + '年' + semesterList[3]
        else:
            current_semester = str(year) + '年' + semesterList[4]
        # 此处待优化,all()
        classInfo_set = ClassInfo.objects.all()
        if id is not None:
            classInfo_set = classInfo_set.filter(id=id)
        if name is not None:
            classInfo_set = classInfo_set.filter(name__icontains=name)
        if cid is not None:
            classInfo_set = classInfo_set.filter(cid=cid)
        if teacher_id is not None:
            classInfo_set = classInfo_set.filter(teacher_id=teacher_id)
        if lesson_id is not None:
            classInfo_set = classInfo_set.filter(lesson_id=lesson_id)
        if semester is not None:
            classInfo_set = classInfo_set.filter(semester__exact=semester)
        if week is not None:
            classInfo_set = classInfo_set.filter(week__contains=week)
        if room is not None:
            classInfo_set = classInfo_set.filter(room__contains=room)

        classInfo_set = classInfo_set.values()

        result = []
        for classInfo in classInfo_set:
            classInfo['current_semester'] = current_semester
            # 每个课程人数属性student_count
            student_count = Class.objects.all().filter(classInfo_id=classInfo['id']).count()
            classInfo['student_count'] = student_count
            result.append(classInfo)

        if len(result) == 0:
            return JsonResponse(
                {'current_semester': current_semester,
                 'code': '4036',
                 'message': status_code['4036']}, safe=False)

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
        插入新的课程信息
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

        # 传入参数为字典数组
        tag = False

        succeed_ids = []
        failed_message = []
        repeated_message = []

        for subjectsDict in subjects:

            name = subjectsDict.get('name', None)
            teacher_id = subjectsDict.get('teacher_id', None)
            semester = subjectsDict.get('semester', None)
            week = subjectsDict.get('week', None)
            room = subjectsDict.get('room', None)
            # lesson_id = subjectsDict.get('lesson_id', None)
            # cid = subjectsDict.get('cid', None)
            # cid设为默认值
            cid = 'default'

            override_tag = subjectsDict.get('override_tag', None)
            if name is None or teacher_id is None or override_tag is None:
                continue
            classInfo = ClassInfo()
            if name is not None:
                # 创建一个同名课程组
                lesson = Lesson()
                lesson.name = name
                lesson.college_id = 1
                lesson.save()
                # 设置初始大项
                initTitleGroup = ['平时', '期中', '期末', '出勤', '加分', '分组']
                weight = int(100 / (len(initTitleGroup) - 3))
                for i in range(len(initTitleGroup)):
                    titleGroup = TitleGroup()
                    titleGroup.name = initTitleGroup[i]
                    if titleGroup.name == '出勤' or titleGroup.name == '加分' or titleGroup.name == '分组':
                        titleGroup.weight = 0
                    else:
                        if i == len(initTitleGroup) - 4:
                            titleGroup.weight = 100 - weight * (len(initTitleGroup) - 4)
                        else:
                            titleGroup.weight = weight
                    titleGroup.lesson = lesson
                    titleGroup.save()
                lesson_id = lesson.id
                classInfo_set = ClassInfo.objects.filter(Q(name=name) & Q(lesson_id=lesson_id))
                if classInfo_set.exists():
                    if override_tag == 1:
                        classInfo_set[0].delete()
                    else:
                        tag = True
                        repeated_message.append({'name': name, 'classInfo_id': classInfo_set[0].id})
                        continue

                classInfo.name = name

            if teacher_id:
                classInfo.teacher_id = teacher_id
            if lesson_id:
                classInfo.lesson_id = lesson_id
            if semester is not None:
                classInfo.semester = semester
            if week is not None:
                classInfo.week = week
            if room is not None:
                classInfo.room = room
            if cid is not None:
                classInfo.cid = cid

            try:
                classInfo.save()
                succeed_ids.append({'id': classInfo.id})
                tag = True
            except Exception as e:
                tag = True
                failed_message.append({'name': name, 'lesson_id': lesson_id})
                continue

        subjects = {
            "succeed_ids": succeed_ids,
            "failed_message": failed_message,
            "repeated_message": repeated_message
        }

        if tag:
            result = {
                'subjects': subjects,
                'code': '2001',
                'message': status_code['2001']
            }
            return JsonResponse(result, safe=False)
        else:
            return insert_failed()

    def update(self, request):
        """
        更新已有课程信息
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
            return JsonResponse({'code': '4032', 'message': status_code['4032']}, safe=False)

        tag = False
        ids = []

        for subjectDict in subjects:
            id = subjectDict.get('id')
            name = subjectDict.get('name')
            teacher_id = subjectDict.get('teacher_id')
            lesson_id = subjectDict.get('lesson_id')
            semester = subjectDict.get('semester')
            week = subjectDict.get('week')
            room = subjectDict.get('room')
            # cid = subjectDict.get('cid')
            cid = 'default'
            if id is None and name is None and teacher_id is None \
                    and semester is None and week is None and cid is None:
                continue

            classInfo_set = ClassInfo.objects.filter(id=id)
            for classInfo in classInfo_set:
                if name:
                    classInfo.name = name
                if teacher_id:
                    classInfo.teacher_id = teacher_id
                if lesson_id:
                    classInfo.lesson_id = lesson_id
                if semester:
                    classInfo.semester = semester
                if week:
                    classInfo.week = week
                if room:
                    classInfo.room = room
                if cid:
                    classInfo.cid = cid

                try:
                    classInfo.save()
                    ids.append({'id': id})
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
        删除符合参数条件的已有课程信息
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
            return JsonResponse({'code': '4032', 'message': status_code['4032']}, safe=False)

        tag = False
        delete_message = []
        for subjectDict in subjects:
            id = subjectDict.get('id')
            if id is None:
                continue
            classInfo_set = ClassInfo.objects.filter(id=id)

            if not classInfo_set.exists():
                continue
            lesson_id = classInfo_set[0].lesson_id
            # lesson = Lesson.objects.filter(id=lesson_id)
            # print(lesson)

            try:
                classInfo_set.delete()
                rest_classInfo_set = ClassInfo.objects.filter(lesson_id=lesson_id)
                Lesson.objects.filter(id=lesson_id).delete()
                tag = True
                delete_message.append({'id': id, 'rest_classInfo_count': rest_classInfo_set.count()})
            except Exception as e:
                continue

        if tag:
            return JsonResponse({'subjects': delete_message, 'code': '2004', 'message': status_code['2004']},
                                safe=False)

        else:
            return delete_failed()

    def getLessonListByTeacherId(self, request):
        """
        根据教师id获得lessonIdList
        :param self:
        :param request:
        :return:
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        teacher_id = request.data['teacher_id']

        if teacher_id is None:
            return JsonResponse({"code": '4032', "message": status_code['4032']})
        lessonIdList = ClassInfo.objects.filter(teacher_id=teacher_id).values('lesson_id').distinct()

        result = []
        for lessonId in list(lessonIdList):
            # 根据lessonId获得lesson
            lesson = Lesson.objects.filter(id=lessonId['lesson_id']).first()
            if lesson is None:
                continue
            else:
                result.append(model_to_dict(lesson))

        if len(result) == 0:
            return JsonResponse(
                {
                    'code': '4036',
                    'message': status_code['4036']}, safe=False)

        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result,
            'count': len(result),
        }

        return JsonResponse(result, safe=False)
