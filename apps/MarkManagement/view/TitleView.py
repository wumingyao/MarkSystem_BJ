#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_Title table.

Here are operations:
get_title_list: GET    http://localhost:8000/api/v1/title/display
         query: GET    http://localhost:8000/api/v1/title/format
        insert: POST   http://localhost:8000/api/v1/title/format
        update: PUT    http://localhost:8000/api/v1/title/format
        remove: DELETE http://localhost:8000/api/v1/title/format
"""

from apps.MarkManagement.view.common import *
from django.db.models import Count
import datetime


class TitleViewSet(viewsets.ViewSet):

    def get_title_list(self, request):
        """
        获取符合参数条件的已有分数小项详细信息
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
        type = request.GET.get('type')
        titleGroup_id = request.GET.get('titleGroup_id')
        classInfo_id = request.GET.get('classInfo_id')

        if id is None and name is None and type is None and titleGroup_id is None and classInfo_id is None:
            return parameter_missed()

        title_set = Title.objects.all()
        if id is not None:
            title_set = title_set.filter(id=id)
        if name is not None:
            title_set = title_set.filter(name=name)
        if type is not None:
            title_set = title_set.filter(type=type)
        if titleGroup_id is not None:
            title_set = title_set.filter(titleGroup_id=titleGroup_id)
        if classInfo_id is not None:
            title_set = title_set.filter(classInfo_id=classInfo_id)

        result = []
        for title in title_set:
            titleDict = model_to_dict(title)

            titleGroup_dict = model_to_dict(title.titleGroup)

            titleDict['titleGroup_id'] = titleDict['titleGroup']
            del titleDict['titleGroup']

            classInfo_dict = model_to_dict(title.classInfo)
            titleDict['classInfo_id'] = titleDict['classInfo']
            del titleDict['classInfo']

            titleDict['titleGroup_message'] = titleGroup_dict
            titleDict['classInfo_message'] = classInfo_dict

            result.append(titleDict)

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
        获取符合参数条件的已有分数小项信息
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
        type = request.GET.get('type')
        titleGroup_id = request.GET.get('titleGroup_id')
        classInfo_id = request.GET.get('classInfo_id')

        if id is None and name is None and type is None and titleGroup_id is None and classInfo_id is None:
            return parameter_missed()

        title_set = Title.objects.all()
        if id is not None:
            title_set = title_set.filter(id=id)
        if name is not None:
            title_set = title_set.filter(name=name)
        if type is not None:
            title_set = title_set.filter(type=type)
        if titleGroup_id is not None:
            title_set = title_set.filter(titleGroup_id=titleGroup_id)
        if classInfo_id is not None:
            title_set = title_set.filter(classInfo_id=classInfo_id)

        # 对象取字典
        title_set = title_set.values()
        result = []
        for title in title_set:
            result.append(title)

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
        插入新的分数小项信息
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
        failed_message = []
        repeated_message = []

        for subjectDict in subjects:
            name = subjectDict.get('name')
            weight = subjectDict.get('weight')
            titleGroup_id = subjectDict.get('titleGroup_id')
            classInfo_id = subjectDict.get('classInfo_id')
            override_tag = subjectDict.get('override_tag')
            if name is None or titleGroup_id is None or classInfo_id is None or override_tag is None:
                continue

            title = Title()
            if name:
                title_set = Title.objects.filter(
                    Q(name=name) & Q(titleGroup_id=titleGroup_id) & Q(classInfo_id=classInfo_id))
                if title_set.exists():
                    if override_tag == 1:
                        title_set[0].delete()
                    else:
                        tag = True
                        repeated_message.append(
                            {'name': name, 'titleGroup_id': titleGroup_id, 'classInfo_id': classInfo_id})
                        continue
                title.name = name

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
                # weight = titleGroup[0]['weight'] / title_count
                weight = 100 / title_count
            if weight:
                title.weight = weight
            if titleGroup_id:
                titleGroup_set = TitleGroup.objects.filter(id=titleGroup_id)

                if not titleGroup_set.exists():
                    continue

                title.titleGroup = titleGroup_set[0]
            if classInfo_id:
                classInfo_set = ClassInfo.objects.filter(id=classInfo_id)

                if not classInfo_set.exists():
                    continue

                title.classInfo = classInfo_set[0]
            try:
                # 更新已经存在的小项权重
                for title_exit in title_exit_set:
                    title_exit.weight = weight
                    title_exit.save(update_fields=['weight'])
                title.save()
                succeed_ids.append({'id': title.id, 'titleGroup_message': model_to_dict(title.titleGroup)})
                try:
                    # 添加一项小项，默认分值，如果属于出勤大项，默认为出勤，其他默认为0
                    # 1、根据classInfo_id在Class表里面查找学生student_id_list
                    # 2、遍历student_id_list
                    # 3、创建Point
                    # 4、根据titleGroup_id 在TitleGroup判断是不是出勤大项
                    Class_List = list(Class.objects.all().filter(classInfo_id=title.classInfo_id).values())
                    for Class_object in Class_List:
                        # 根据titleGroup_id在TitleGroup判断是不是出勤大项
                        titleGroup = TitleGroup.objects.filter(id=title.titleGroup_id).first()
                        if titleGroup.name == '出勤' or titleGroup.name == '分组':
                            pointNumber = 1
                        elif titleGroup.name == '加分':
                            pointNumber = None
                        else:
                            pointNumber = 0
                        point = Point()
                        point.pointNumber = pointNumber
                        point.date = datetime.datetime.now()
                        point.note = ' '

                        classInfo_id = Class_object['classInfo_id']
                        if classInfo_id:
                            classInfo_set = ClassInfo.objects.filter(id=classInfo_id)

                            if not classInfo_set.exists():
                                continue

                            point.classInfo = classInfo_set[0]

                        student_id = Class_object['student_id']
                        if student_id:
                            student_set = Student.objects.filter(id=student_id)

                            if not student_set.exists():
                                continue

                            point.student = student_set[0]
                        title_id = title.id
                        if title_id:
                            title_set = Title.objects.filter(id=title_id)

                            if title_set.exists() == 0:
                                continue

                            point.title = title_set[0]
                        point.save()
                except Exception as e:
                    print("error:", e)
                tag = True
            except Exception as e:
                tag = True
                failed_message.append({'name': name, 'titleGroup_id': titleGroup_id, 'classInfo_id': classInfo_id})
                continue
        subjects = {
            "succeed_ids": succeed_ids,
            "failed_message": failed_message,
            "repeated_message": repeated_message
        }

        if tag:
            return JsonResponse({'subjects': subjects, 'code': '2001', 'message': status_code['2001']}, safe=False)
        else:
            return insert_failed()

    def update(self, request):
        """
        更新已有分数小项信息
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
            weight = subjectDict.get('weight')
            titleGroup_id = subjectDict.get('titleGroup_id')
            classInfo_id = subjectDict.get('classInfo_id')
            title_set = Title.objects.filter(id=id)

            for title in title_set:
                if name:
                    title.name = name
                if type:
                    title.type = type
                if weight:
                    title.weight = weight
                if titleGroup_id:
                    titleGroup_set = TitleGroup.objects.filter(id=titleGroup_id)

                    if not titleGroup_set.exists():
                        continue

                    title.titleGroup = titleGroup_set[0]
                if classInfo_id:
                    classInfo_set = ClassInfo.objects.filter(id=classInfo_id)

                    if not classInfo_set.exists():
                        continue

                    title.classInfo = classInfo_set[0]

                try:
                    title.save()
                    ids.append({'id': title.id})
                    tag = True
                except Exception as e:
                    continue

        if tag:
            return JsonResponse({'subjects': ids, 'code': '2005', 'message': status_code['2005']}, safe=False)

        else:
            return update_failed()

    def remove(self, request):
        """
        删除符合参数条件的已有分数小项信息
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

            title_set = Title.objects.filter(id=id)

            if not title_set.exists():
                continue

            # 根据title的id获得titleGroup_id和 classInfo_id
            titleGroup_id = title_set.values()[0]['titleGroup_id']
            classInfo_id = title_set.values()[0]['classInfo_id']

            # 计算大项占比
            titleGroup = list(TitleGroup.objects.filter(id=titleGroup_id).values())
            # 查找已经存在的小项
            title_exit_set = Title.objects.filter(
                Q(titleGroup_id=titleGroup_id) & Q(classInfo_id=classInfo_id) & ~Q(id=id))
            # 小项权重自动平均，计算classInfo_id的小项有多少项title_count
            title_count = len(list(title_exit_set))
            if (len(titleGroup) <= 0):
                continue
            if title_count == 0:
                weight = 0
            else:
                # weight = titleGroup[0]['weight'] / title_count
                weight = 100 / title_count
            try:
                # 更新已经存在的小项权重
                for title_exit in title_exit_set:
                    title_exit.weight = weight
                    title_exit.save(update_fields=['weight'])
                title_set.delete()
                tag = True
            except Exception as e:
                continue

        if tag:
            return delete_succeed()
        else:
            return delete_failed()
