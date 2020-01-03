#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import the excel table into database

"""
This file is for the operation of import data from the browser into database.

Here is the operation:
insert: POST http://localhost:8000/api/v1/point/import_data
"""

from apps.MarkManagement.view.common import *


class ImportDataViewSet(viewsets.ViewSet):

    def insert(self, request):
        """
        Insert the import data from the browser into database.
        :param request: the request from browser. 用来获取access_token和插入内容
        :return: JSON response. 包括code, message, subjects(opt), count(opt)
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
        result = {}
        error_title_message = []
        exist_title_message = []

        exist_point_message = []
        error_point_message = []

        succeed_title_message = []
        succeed_point_message = []

        title_list = post_data.get('title_list')
        point_list = post_data.get('point_list')
        lesson_id = post_data.get('lesson_id')
        sid_list = post_data.get('sid_list')

        # 1.拿到所有的classInfo_id，即得到学生所在课程id集合
        classInfo_id_set = set()
        for sid in sid_list:
            classInfo_set = ClassInfo.objects.filter(Q(lesson_id=lesson_id) & Q(class__student__sid=sid))
            for classInfo in classInfo_set:
                classInfo_id_set.add(classInfo.id)

        if len(classInfo_id_set) == 0:
            return insert_failed()

        # 2.插入Title
        for classInfo_id in classInfo_id_set:
            for title_message in title_list:
                title_name = title_message['name']
                titleGroup_id = title_message['titleGroup_id']

                title_set = Title.objects.filter(
                    Q(name=title_name) & Q(titleGroup_id=titleGroup_id) & Q(classInfo_id=classInfo_id))
                if title_set.exists():
                    exist_title_message.append({'name': title_set[0].name})
                    print("already exists")
                    continue
                new_title = Title()
                new_title.name = title_name
                new_title.titleGroup_id = titleGroup_id
                new_title.classInfo_id = classInfo_id

                # 查找已经存在的小项
                title_exit_set = Title.objects.filter(Q(titleGroup_id=titleGroup_id) & Q(classInfo_id=classInfo_id))
                # 小项权重自动平均，计算classInfo_id的小项有多少项title_count
                title_count = len(list(title_exit_set)) + 1
                # 计算大项占比
                titleGroup = list(TitleGroup.objects.filter(id=titleGroup_id).values())
                if (len(titleGroup) <= 0):
                    continue
                if title_count == 0:
                    weight = 0
                else:
                    weight = 100 / title_count
                # new_title.weight = title_message['weight']
                new_title.weight = weight
                try:
                    # 更新已经存在的小项权重
                    for title_exit in title_exit_set:
                        title_exit.weight = weight
                        title_exit.save(update_fields=['weight'])
                    new_title.save()
                    titleDict = model_to_dict(new_title)

                    titleGroup_dict = model_to_dict(new_title.titleGroup)
                    titleDict['titleGroup_id'] = titleDict['titleGroup']
                    del titleDict['titleGroup']

                    classInfo_dict = model_to_dict(new_title.classInfo)
                    titleDict['classInfo_id'] = titleDict['classInfo']
                    del titleDict['classInfo']

                    titleDict['titleGroup_message'] = titleGroup_dict
                    titleDict['classInfo_message'] = classInfo_dict

                    succeed_title_message.append(titleDict)
                    print(new_title.id)
                except Exception as e:
                    error_title_message.append({'name': title_name})

        # 3.插入分数
        for point_message in point_list:
            sid = point_message['sid']
            title_name = point_message['title_name']
            titleGroup_id = point_message['titleGroup_id']

            # 3.1拿到classInfo_id
            # 此处classInfo_set实际只有一个值
            classInfo_set = ClassInfo.objects.filter(Q(lesson_id=lesson_id) & Q(class__student__sid=sid))
            if not classInfo_set.exists():
                error_point_message.append(point_message)
                continue

            classInfo_id = classInfo_set[0].id
            title_set = Title.objects.filter(
                Q(name=title_name) & Q(titleGroup_id=titleGroup_id) & Q(classInfo_id=classInfo_id))

            if not title_set.exists():
                continue

            title_id = title_set[0].id

            pointNumber = point_message['pointNumber']

            student_set = Student.objects.filter(sid=sid)
            point_set = Point.objects.filter(
                Q(classInfo_id=classInfo_id) & Q(title_id=title_id) & Q(student_id=student_set[0].id))

            if point_set.exists():
                point = point_set[0]
                point.pointNumber = pointNumber
                point.save()
                print(point.id)
                exist_point_message.append(point_message)
                continue

            point = Point()
            point.title_id = title_id
            point.pointNumber = pointNumber
            point.classInfo_id = classInfo_id
            point.student_id = student_set[0].id

            try:
                point.save()

                pointDict = model_to_dict(point)

                student_dict = model_to_dict(point.student)
                title_dict = model_to_dict(point.title)
                classInfo_dict = model_to_dict(point.classInfo)

                pointDict['student_id'] = pointDict['student']
                del pointDict['student']

                pointDict['title_id'] = pointDict['title']
                del pointDict['title']

                pointDict['classInfo_id'] = pointDict['classInfo']
                del pointDict['classInfo']

                pointDict['student_message'] = student_dict
                pointDict['title_message'] = title_dict
                pointDict['classInfo_message'] = classInfo_dict

                succeed_point_message.append(pointDict)
            except Exception as e:
                error_point_message.append(point_message)
                continue

        result['succeed_point_message'] = succeed_point_message
        result['succeed_title_message'] = succeed_title_message

        result['exists_title_message'] = exist_title_message
        result['exists_point_message'] = exist_point_message

        result['error_title_message'] = error_title_message
        result['error_point_message'] = error_point_message

        code_number = '2001'

        if len(error_title_message) or len(exist_title_message) or len(error_point_message) or len(exist_point_message):
            code_number = '2019'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result,
            'count': len(result),
        }

        return JsonResponse(result, safe=False)
