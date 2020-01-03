#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is for the operation of t_Point table.

Here are operations:
get_point_list: GET    http://localhost:8000/api/v1/point/display
         query: GET    http://localhost:8000/api/v1/point/format
        insert: POST   http://localhost:8000/api/v1/point/format
        update: PUT    http://localhost:8000/api/v1/point/format
        remove: DELETE http://localhost:8000/api/v1/point/format
"""
from apps.MarkManagement.view.common import *
from django.db.models import Avg, Sum, Max, Min, Count, F, FloatField
import numpy as np
import warnings
import time

warnings.filterwarnings("ignore")


class PointViewSet(viewsets.ViewSet):

    # 成绩导出接口
    def output(self, request):
        """
        :param request: classInfo_id
        :return: 返回导出成绩接口
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()
        classInfo_id = request.GET.get('classInfo_id')
        if classInfo_id is None:
            return parameter_missed()
        tableHead = ['学号', '姓名']
        firstVal = ['sid', 'name']
        title_id_Names = list(Title.objects.filter(classInfo_id=classInfo_id).values('id', 'name'))
        for title_id_Name in title_id_Names:
            tableHead.append(title_id_Name['name'])
            firstVal.append(str(title_id_Name['id']))
        pointSets = Point.objects.filter(classInfo_id=classInfo_id).values('student__sid', 'student__name',
                                                                           'title__id', 'pointNumber',
                                                                           'title__titleGroup__name')
        sidList = list(Class.objects.filter(classInfo_id=classInfo_id).values('student__sid'))
        students = []
        for sid in sidList:
            sid = sid['student__sid']
            StudentName = pointSets.filter(student__sid=sid).values('student__name').first()['student__name']
            student = {'sid': sid, 'name': StudentName}
            pointNumbers = list(
                pointSets.filter(student__sid=sid).values('title__id', 'pointNumber', 'title__titleGroup__name'))
            for pointNumber in pointNumbers:
                # 出勤转换
                if pointNumber['title__titleGroup__name'] == '出勤':
                    if pointNumber['pointNumber'] == 1:
                        pointNumber['pointNumber'] = '出勤'
                    elif pointNumber['pointNumber'] == 2:
                        pointNumber['pointNumber'] = '缺勤'
                    elif pointNumber['pointNumber'] == 3:
                        pointNumber['pointNumber'] = '请假'
                    elif pointNumber['pointNumber'] == 4:
                        pointNumber['pointNumber'] = '迟到'
                    else:
                        pointNumber['pointNumber'] = '其他'
                student[pointNumber['title__id']] = pointNumber['pointNumber']
            students.append(student)
        result = {
            'tableHead': tableHead,
            'firstVal': firstVal,
            'tableData': students
        }
        if len(result['tableData']) == 0:
            return query_failed()
        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result
        }

        return JsonResponse(result, safe=False)

    # 成绩分析接口
    def getWeightData(self, request):
        """
        :param request: 请求收到classInfo_id
        :return: 返回成绩分析页面所需的信息
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()
        classInfo_id = request.GET.get('classInfo_id')
        if classInfo_id is None:
            return parameter_missed()
        # 根据classInfo_id查询title
        # titles = Title.objects.filter(
        #     Q(classInfo_id=classInfo_id) & ~Q(titleGroup__name='出勤') & ~Q(titleGroup__name='加分') & ~Q(
        #         titleGroup__name='分组') & ~Q(titleGroup__name='其他'))
        titles = list(Point.objects.filter(
            Q(classInfo_id=classInfo_id) & ~Q(title__titleGroup__name='出勤') & ~Q(title__titleGroup__name='加分') & ~Q(
                title__titleGroup__name='分组') & ~Q(title__titleGroup__name='其他')).values('title__id', 'title__name',
                                                                                         'title__weight',
                                                                                         'title__classInfo__id',
                                                                                         'title__classInfo__id').annotate(
            titleAverage=Avg('pointNumber')).values('title__id', 'title__name', 'title__weight', 'title__classInfo__id',
                                                    'title__classInfo__id', 'titleAverage'))

        # 该班级总人数
        total = Class.objects.filter(classInfo_id=classInfo_id).aggregate(count=Count('student_id', distinct=True))[
            'count']
        # 计算该班级每个学生各个大项的分数
        TitleGroupPerStudent = Point.objects.filter(
            Q(classInfo_id=classInfo_id) & ~Q(title__titleGroup__name='出勤') & ~Q(title__titleGroup__name='加分') & ~Q(
                title__titleGroup__name='分组') & ~Q(title__titleGroup__name='其他')).values('title__titleGroup__id',
                                                                                         'title__titleGroup__weight',
                                                                                         'student_id').annotate(
            titleAverage=Avg('pointNumber')).values('title__titleGroup__id', 'title__titleGroup__weight', 'student_id',
                                                    'titleAverage')
        student_idList = list(Class.objects.filter(classInfo_id=classInfo_id).values('student_id'))
        # 不及格人数
        count_60 = 0
        count_70 = 0
        count_80 = 0
        count_90 = 0
        count_100 = 0
        for student_id in student_idList:
            id = student_id['student_id']
            name = Student.objects.filter(id=id).values('name')
            # A.objects.all().aggregate(ab_sum=Sum(F('a') * F('b'), output_field=FloatField()))
            pointTotal = TitleGroupPerStudent.filter(student_id=id).aggregate(
                total=Sum(F('titleAverage') * F('title__titleGroup__weight'), output_field=FloatField()))['total'] / 100
            if pointTotal < 60:
                count_60 = count_60 + 1
            elif pointTotal < 70:
                count_70 = count_70 + 1
            elif pointTotal < 80:
                count_80 = count_80 + 1
            elif pointTotal < 90:
                count_90 = count_90 + 1
            else:
                count_100 = count_100 + 1

        # 计算及格率
        if total <= 0:
            rate = 0
        else:
            rate = 1 - count_60 / total

        # 计算各分数段的人数
        gradeSection = [count_60, count_70, count_80, count_90, count_100]
        # 按照大项求平均分
        TitleGroupavgs = Point.objects.filter(
            Q(classInfo_id=classInfo_id) & ~Q(title__titleGroup__name='出勤') & ~Q(title__titleGroup__name='加分') & ~Q(
                title__titleGroup__name='分组') & ~Q(title__titleGroup__name='其他')).values('title__titleGroup__id',
                                                                                         'title__titleGroup__weight').annotate(
            titleAverage=Avg('pointNumber')).values('title__titleGroup__id', 'title__titleGroup__weight',
                                                    'titleAverage')
        avg = 0
        for TitleGroupavg in list(TitleGroupavgs):
            avg = avg + float(TitleGroupavg['title__titleGroup__weight']) / 100 * TitleGroupavg['titleAverage']

        result = {
            'titles': titles,
            'total': total,
            'avg': avg,
            'rate': rate,
            'gradeSection': gradeSection
        }
        if len(titles) == 0:
            return query_failed()
        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result
        }

        return JsonResponse(result, safe=False)

    def get_AllClass_TitleGroup_Avgpiont(self, request):
        """
        根据lesson_id 获得该课程组的所有班级的所有大项的平均分
        :param request: the request from browser. 用来获取access_token和查询条件
        :return:JSON response. 包括code, message, subjects(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果所有参数为空，即Params中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试查询
                    查询失败，返回query_failed的JSON response
                    查询成功，返回JSON response包括code, message, subjects状态码2000
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()
        lesson_id = request.GET.get('lesson_id')
        if lesson_id is None:
            return parameter_missed()
        # 获得classInfo_List
        classInfo_List = list(ClassInfo.objects.filter(lesson_id=lesson_id).values())
        # 获得TitleGroup_List
        titleGroup_List = list(TitleGroup.objects.filter(lesson_id=lesson_id).values())

        # 对于每个班级
        classInfo_TitleGroup_AvgPoint_List = []
        for classInfo in classInfo_List:
            classInfo_id = classInfo['id']
            classInfo_TitleGroup_AvgPoint = {}
            classInfo_TitleGroup_AvgPoint['classInfo'] = classInfo
            # 对于每个大项
            for titleGroup in titleGroup_List:
                if titleGroup['name'] == '加分' or titleGroup['name'] == '出勤':
                    continue
                titleGroup_id = titleGroup['id']
                title_List = list(
                    Title.objects.filter(Q(classInfo_id=classInfo_id) & Q(titleGroup_id=titleGroup_id)).values())
                pointNumber_Avg_List = []
                for title in title_List:
                    pointNumber_Avg = list(Point.objects.filter(
                        Q(title_id=title['id']) & Q(classInfo_id=classInfo_id)).aggregate(Avg('pointNumber')).values())
                    pointNumber_Avg_List.append(pointNumber_Avg)
                classInfo_TitleGroup_AvgPoint[str(titleGroup_id)] = np.mean(sum(pointNumber_Avg_List, []))
            classInfo_TitleGroup_AvgPoint_List.append(classInfo_TitleGroup_AvgPoint)
        result = classInfo_TitleGroup_AvgPoint_List
        if len(result) == 0:
            return query_failed()
        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result
        }

        return JsonResponse(result, safe=False)

    def get_Count_point(self, request):
        """
        :param request: he request from browser. 用来获取access_token和查询条件
        :return: JSON response. 包括code, message, subjects(opt)
                result:返回一个数组，里面包含0-60 60-70 70-80 80-90 90-100 的人数
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果所有参数为空，即Params中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试查询
                    查询失败，返回query_failed的JSON response
                    查询成功，返回JSON response包括code, message, subjects, count，状态码2000
        """
        """
        前端传来 classinfo_id 和title_id 返回一个数组，里面包含0-60 60-70 70-80 80-90 90-100 的人数
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()
        classInfo_id = request.GET.get('classInfo_id')
        title_id = request.GET.get('title_id')
        # 里面包含0 - 60 60 - 70 70 - 80 80 - 90 90 - 100 的人数
        # 如果参数丢失
        if classInfo_id is None and title_id is None:
            return parameter_missed()

        # 根据classinfo_id和title_id查询各阶段分数人数
        point_set = Point.objects.all()
        if classInfo_id is not None:
            point_set = point_set.filter(classInfo_id=classInfo_id)
        if title_id is not None:
            point_set = point_set.filter(title_id=title_id)
        count_60 = point_set.filter(pointNumber__lt=60).count()
        count_70 = point_set.filter(Q(pointNumber__gte=60) & Q(pointNumber__lt=70)).count()
        count_80 = point_set.filter(Q(pointNumber__gte=70) & Q(pointNumber__lt=80)).count()
        count_90 = point_set.filter(Q(pointNumber__gte=80) & Q(pointNumber__lt=90)).count()
        count_100 = point_set.filter(Q(pointNumber__gte=90)).count()

        result = [count_60, count_70, count_80, count_90, count_100]
        if len(result) == 0:
            return query_failed()
        code_number = '2000'
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': result
        }

        return JsonResponse(result, safe=False)

    def get_point_list(self, request):
        """
        Get t_Point table list
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
        classInfo_id = request.GET.get('classInfo_id')
        student_id = request.GET.get('student_id')
        title_id = request.GET.get('title_id')
        date = request.GET.get('date')
        note = request.GET.get('note')

        if id is None and classInfo_id is None and student_id is None \
                and title_id is None and date is None and note is None:
            return parameter_missed()

        point_set = Point.objects.all()
        if id is not None:
            point_set = point_set.filter(id=id)
        if student_id is not None:
            point_set = point_set.filter(student_id=student_id)
        if title_id is not None:
            point_set = point_set.filter(title_id=title_id)
        if date is not None:
            point_set = point_set.filter(date=date)
        if note is not None:
            point_set = point_set.filter(note=note)
        if classInfo_id:
            point_set = point_set.filter(classInfo_id=classInfo_id)

        result = []
        result = list(point_set.values())
        # for point in list(point_set.values()):
        # pointDict = model_to_dict(point)
        #
        # student_dict = model_to_dict(point.student)
        # title_dict = model_to_dict(point.title)
        # classInfo_dict = model_to_dict(point.classInfo)
        #
        # pointDict['student_id'] = pointDict['student']
        # del pointDict['student']
        #
        # pointDict['title_id'] = pointDict['title']
        # del pointDict['title']
        #
        # pointDict['classInfo_id'] = pointDict['classInfo']
        # del pointDict['classInfo']
        #
        # pointDict['student_message'] = student_dict
        # pointDict['title_message'] = title_dict
        # pointDict['classInfo_message'] = classInfo_dict

        # result.append(point)

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
        Query t_Point table
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
        classInfo_id = request.GET.get('classInfo_id')
        student_id = request.GET.get('student_id')
        title_id = request.GET.get('title_id')
        date = request.GET.get('date')
        note = request.GET.get('note')
        start = time.time()
        if id is None and classInfo_id is None and student_id is None \
                and title_id is None and date is None and note is None:
            return parameter_missed()

        point_set = Point.objects.filter(classInfo_id=classInfo_id).values('id', 'pointNumber', 'date', 'note',
                                                                           'classInfo_id', 'student_id', 'title_id',
                                                                           'title__titleGroup__name')
        if id is not None:
            point_set = point_set.filter(id=id).values('id', 'pointNumber', 'date', 'note',
                                                       'classInfo_id', 'student_id', 'title_id',
                                                       'title__titleGroup__name')
        if student_id is not None:
            point_set = point_set.filter(student_id=student_id).values('id', 'pointNumber', 'date', 'note',
                                                                       'classInfo_id', 'student_id', 'title_id',
                                                                       'title__titleGroup__name')
        if title_id is not None:
            point_set = point_set.filter(title_id=title_id).values('id', 'pointNumber', 'date', 'note',
                                                                   'classInfo_id', 'student_id', 'title_id',
                                                                   'title__titleGroup__name')
        if date is not None:
            point_set = point_set.filter(date=date).values('id', 'pointNumber', 'date', 'note',
                                                           'classInfo_id', 'student_id', 'title_id',
                                                           'title__titleGroup__name')
        if note is not None:
            point_set = point_set.filter(note=note).values('id', 'pointNumber', 'date', 'note',
                                                           'classInfo_id', 'student_id', 'title_id',
                                                           'title__titleGroup__name')
        if classInfo_id:
            point_set = point_set.filter(classInfo_id=classInfo_id).values('id', 'pointNumber', 'date', 'note',
                                                                           'classInfo_id', 'student_id', 'title_id',
                                                                           'title__titleGroup__name')
        end = time.time()
        # 对象取字典
        # point_set = point_set.values()
        result = list(point_set)

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
        Insert t_Point table
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

        succeed_ids = []
        failed_message = []
        repeated_ids = []

        for subjectDict in subjects:
            classInfo_id = subjectDict.get('classInfo_id')
            student_id = subjectDict.get('student_id')
            title_id = subjectDict.get('title_id')
            date = subjectDict.get('date')
            note = subjectDict.get('note')
            pointNumber = subjectDict.get('pointNumber')

            if classInfo_id is None or student_id is None or title_id is None or pointNumber is None:
                continue

            exist_point_set = Point.objects.filter(Q(student_id=student_id) & Q(title_id=title_id))

            if exist_point_set.exists():
                repeated_ids.append({'id': exist_point_set[0].id})
                continue

            point = Point()

            if classInfo_id:
                classInfo_set = ClassInfo.objects.filter(id=classInfo_id)

                if not classInfo_set.exists():
                    continue

                point.classInfo = classInfo_set[0]

            if student_id:
                student_set = Student.objects.filter(id=student_id)

                if not student_set.exists():
                    continue

                point.student = student_set[0]

            if title_id:
                title_set = Title.objects.filter(id=title_id)

                if title_set.exists() == 0:
                    continue

                point.title = title_set[0]

            if date:
                point.date = date
            if note:
                point.note = note
            if pointNumber:
                point.pointNumber = pointNumber

            try:
                point.save()
                succeed_ids.append({'id': point.id})
                tag = True
            except Exception as e:
                failed_message.append({'student_id': student_id, 'title_id': title_id})
                continue

        subjects = {
            "succeed_ids": succeed_ids,
            "failed_message": failed_message,
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
        Update t_Point table
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
            classInfo_id = subjectDict.get('classInfo_id')
            student_id = subjectDict.get('student_id')
            title_id = subjectDict.get('title_id')
            date = subjectDict.get('date')
            note = subjectDict.get('note')
            pointNumber = subjectDict.get('pointNumber')

            if id is None and classInfo_id is None and student_id is None and title_id is None:
                continue

            point_set = Point.objects.filter(id=id)
            if classInfo_id:
                point_set = point_set.filter(classInfo_id=classInfo_id)
            if student_id:
                point_set = point_set.filter(student_id=student_id)
            if title_id:
                point_set = point_set.filter(title_id=title_id)

            for point in point_set:
                if classInfo_id:
                    classInfo_set = ClassInfo.objects.filter(id=classInfo_id)

                    if not classInfo_set.exists():
                        continue

                    point.classInfo = classInfo_set[0]

                if student_id:
                    student_set = Student.objects.filter(id=student_id)

                    if not student_set.exists():
                        continue

                    point.student = student_set[0]

                if title_id:

                    title_set = Title.objects.filter(id=title_id)

                    if not title_set.exists():
                        continue

                    point.title = title_set[0]

                if date:
                    point.date = date
                if note:
                    point.note = note
                if pointNumber is not None:
                    point.pointNumber = pointNumber

                try:
                    point.save()
                    ids.append({'id': point.id})
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
        Remove t_Point table
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

            point_set = Point.objects.filter(id=id)

            if not point_set.exists():
                continue

            try:
                point_set.delete()
                tag = True
            except Exception as e:
                continue

        if tag:
            return delete_succeed()
        else:
            return delete_failed()
