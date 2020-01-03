#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_TitleGroup table.

Here are operations:
 query: GET    http://localhost:8000/api/v1/titleGroup/format
insert: POST   http://localhost:8000/api/v1/titleGroup/format
update: PUT    http://localhost:8000/api/v1/titleGroup/format
remove: DELETE http://localhost:8000/api/v1/titleGroup/format
"""
from apps.MarkManagement.view.common import *


class TitleGroupViewSet(viewsets.ViewSet):

    def query(self, request):
        """
        获取符合参数条件的已有分数大项信息
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
        lesson_id = request.GET.get('lesson_id')
        weight = request.GET.get('weight')

        if id is None and name is None and lesson_id is None and weight is None:
            return parameter_missed()

        titleGroup_set = TitleGroup.objects.all()
        if id is not None:
            titleGroup_set = titleGroup_set.filter(id=id)
        if name is not None:
            titleGroup_set = titleGroup_set.filter(name=name)
        if lesson_id is not None:
            titleGroup_set = titleGroup_set.filter(lesson_id=lesson_id)
        if weight is not None:
            titleGroup_set = titleGroup_set.filter(weight=weight)

        # 对象取字典
        titleGroup_set = titleGroup_set.values()

        result = []
        for titleGroup in titleGroup_set:
            result.append(titleGroup)

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
        插入新的分数大项信息
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
            lesson_id = subjectDict.get('lesson_id')
            override_tag = subjectDict.get('override_tag')

            if name is None or lesson_id is None or override_tag is None:
                continue

            titleGroup = TitleGroup()
            if name:
                titleGroup_set = TitleGroup.objects.filter(Q(name=name) & Q(lesson_id=lesson_id))
                if titleGroup_set.exists():
                    if override_tag == 1:
                        titleGroup_set[0].delete()
                    else:
                        repeated_message.append({'name': name, 'lesson_id': lesson_id})
                        continue
                titleGroup.name = name
            if weight:
                titleGroup.weight = weight
            if lesson_id:
                lesson_set = Lesson.objects.filter(id=lesson_id)
                if not lesson_set.exists():
                    continue
                titleGroup.lesson = lesson_set[0]

            try:
                titleGroup.save()

                succeed_ids.append({'id': titleGroup.id})
                tag = True
            except Exception as e:
                failed_message.append({'name': name, 'lesson_id': lesson_id})
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
        更新已有分数大项信息
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
            lesson_id = subjectDict.get('lesson_id')
            titleGroup_set = TitleGroup.objects.filter(id=id)

            for titleGroup in titleGroup_set:
                if name is not None:
                    titleGroup.name = name
                if weight is not None:
                    titleGroup.weight = weight
                if lesson_id is not None:
                    lesson_set = Lesson.objects.filter(id=lesson_id)
                    if not lesson_set.exists():
                        continue
                    titleGroup.lesson = lesson_set[0]
                try:
                    titleGroup.save()
                    ids.append({'id': titleGroup.id})
                    tag = True
                except Exception as e:
                    continue

        if tag:
            return JsonResponse({'subjects': ids, 'code': '2005', 'message': status_code['2005']}, safe=False)
        else:
            return update_failed()

    def remove(self, request):
        """
        删除符合参数条件的已有分数大项信息
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

        for subjectDict in subjects:
            id = subjectDict.get('id')
            if id is None:
                continue
            titleGroup_set = TitleGroup.objects.filter(id=id)

            if not titleGroup_set.exists():
                continue

            try:
                titleGroup_set.delete()
                tag = True
            except Exception as e:
                continue

        if tag:
            return delete_succeed()
        else:
            return delete_failed()
