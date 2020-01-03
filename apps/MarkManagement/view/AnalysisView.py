#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apps.MarkManagement.view.common import *
import numpy as np
import math
from django.db.models import Avg


class AnalysisViewSet(viewsets.ViewSet):
    # 分析各种考试对提高学位英语成绩的贡献值
    def Analysisfun(self, request):
        """ 增益熵
            描述x对y的熵增益情况
             """

        # 计算熵
        def entropy(x):
            set_value_x = set(x)
            ent = 0.0
            for x_value in set_value_x:
                p = float(x.count(x_value)) / len(x)
                logp = np.log2(p)
                ent -= p * logp
            return ent

        # 条件熵
        def ent_condition(x, y):
            set_value_x = set(x)
            ent = 0.0
            for x_value in set_value_x:
                sub_y = [y[i] for i in range(len(x)) if x[i] == x_value]
                ent += (float(len(sub_y)) / len(y)) * entropy(sub_y)
            return ent

        # 熵增益
        def gain_ent(x, y):
            x = list(x)
            y = list(y)
            # y的熵
            ent_y = entropy(y)
            # x条件下y的熵
            ent_y_con_x = ent_condition(x, y)
            gain = ent_y - ent_y_con_x
            return gain

        """ 熵增益结束"""
        """ 信息增益比 """

        def gainRate_ent(x, y):
            xe = entropy(list(x))
            yxe = gain_ent(x, y)
            if xe == 0:
                return 0
            else:
                return yxe / xe

        """ Pearson系数 
            皮尔逊系数描述了两个变量之间的相关程度
            取值范围[-1,1],0表示两个变量之间无关
            """

        def coef_Pearson(x, y):
            x = list(x)
            y = list(y)
            mean_x = np.mean(x)
            mean_y = np.mean(y)
            n = len(x)
            # 协方差
            cov = 0.0
            sumBottom = 0.0
            # x,y方差
            var_x = 0.0
            var_y = 0.0
            for i in range(n):
                cov += (x[i] - mean_x) * (y[i] - mean_y)
            for i in range(n):
                var_x += math.pow(x[i] - mean_x, 2)
            for i in range(n):
                var_y += math.pow(y[i] - mean_y, 2)
            return cov / math.sqrt(var_x * var_y)

        # 从数据库获取数据
        # 获取数据库中某个学期semester的所有分数
        def getAllScores(titleGroupId):

            titleGroup = TitleGroup.objects.filter(id=titleGroupId).first()
            # 属于同一个lessonId下的除了titleGroup以外的所有titleGroups
            otherTiltleGroupList = list(
                TitleGroup.objects.filter(Q(lesson_id=titleGroup.lesson_id) & ~Q(id=titleGroup.id)).values())
            # 获得该lesson下的所有学生studentID
            studentIdList = list(
                Class.objects.filter(classInfo__lesson_id=titleGroup.lesson_id).values('student_id'))

            result = []
            for othertitleGroup in otherTiltleGroupList:
                pointList = []
                pointMap = {}
                # 计算每一位学生该大项的成绩
                for studentId in studentIdList:
                    point = Point.objects.filter(
                        Q(student_id=studentId['student_id']) & Q(
                            title__titleGroup_id=othertitleGroup['id'])).aggregate(Avg('pointNumber'))
                    if point['pointNumber__avg'] is None:
                        point['pointNumber__avg'] = 0
                    pointList.append(point['pointNumber__avg'])
                pointMap[othertitleGroup['name']] = pointList
                result.append(pointMap)
            targetPointList = []
            for studentId in studentIdList:
                point = Point.objects.filter(
                    Q(student_id=studentId['student_id']) & Q(
                        title__titleGroup_id=titleGroup.id)).aggregate(Avg('pointNumber'))
                if point['pointNumber__avg'] is None:
                    point['pointNumber__avg'] = 0
                targetPointList.append(point['pointNumber__avg'])
            return result, targetPointList
            # temps = []
            # dicts = {}
            # results = []

            # improve the performance
            # point_set = Point.objects.filter(classInfo__semester=semester) \
            #     .values('student', 'pointNumber', 'title__name', 'title__titleGroup__name')

            # print('point_set length=', len(point_set))
            # point_set = []
            # for point in point_set:
            #     if point['title__titleGroup__name'] == '期中客观分':
            #         if point['title__name'] == '期中词汇':
            #             point['vocabulary'] = point['pointNumber']
            #         if point['title__name'] == '期中听力':
            #             point['hearing'] = point['pointNumber']
            #         if point['title__name'] == '期中翻译':
            #             point['translate'] = point['pointNumber']
            #         if point['title__name'] == '期中写作':
            #             point['writing'] = point['pointNumber']
            #         if point['title__name'] == '期中细节':
            #             point['details'] = point['pointNumber']
            #     if point['title__titleGroup__name'] == '期中主观分':
            #         point['subjective_qz'] = point['pointNumber']
            #     if point['title__titleGroup__name'] == '期末客观分':
            #         point['objective_qm'] = point['pointNumber']
            #     if point['title__titleGroup__name'] == '期末主观分':
            #         point['subjective_qm'] = point['pointNumber']
            #
            #     elif point['title__titleGroup__name'] in ['学位主观分', '学位客观分']:
            #         point['xuewei'] = point['pointNumber']
            #
            #     del point['pointNumber']
            #     del point['title__titleGroup__name']
            #     del point['title__name']
            #     temps.append(point)
            #
            # for temp in temps:
            #     if temp['student'] in dicts:
            #         if 'xuewei' in dicts[temp['student']] and 'xuewei' in temp:
            #             dicts[temp['student']]['xuewei'] += temp['xuewei']
            #         else:
            #             dicts[temp['student']].update(temp)
            #     else:
            #         dicts[temp['student']] = temp
            #
            # for value in dicts.values():
            #     if value != {}:
            #         if 'vocabulary' not in value:
            #             value['vocabulary'] = 0
            #         if 'hearing' not in value:
            #             value['hearing'] = 0
            #         if 'translate' not in value:
            #             value['translate'] = 0
            #         if 'writing' not in value:
            #             value['writing'] = 0
            #         if 'details' not in value:
            #             value['details'] = 0
            #         if 'subjective_qz' not in value:
            #             value['subjective_qz'] = 0
            #         if 'objective_qm' not in value:
            #             value['objective_qm'] = 0
            #         if 'subjective_qm' not in value:
            #             value['subjective_qm'] = 0
            #         if 'xuewei' not in value:
            #             value['xuewei'] = 0
            #
            #         results.append(value)
            #
            # for result in results:
            #     del result['student']
            #
            # return results

        # 从前端读到数据
        titleGroupId = request.data['titleGroupId']

        scoresList, targetPointList = getAllScores(titleGroupId)

        resultMap = {}
        for score in scoresList:
            # print('key=', list(score.keys())[0])
            # print('value=', list(score.values())[0])
            # print('targetPointList=', targetPointList)
            key = list(score.keys())[0]
            if key is None:
                continue
            resultMap[key] = round(gainRate_ent(list(score.values())[0], targetPointList), 6)
        #     vocabulary.append(scoresListMap[i]['vocabulary'])
        #     hearing.append(scoresListMap[i]['hearing'])
        #     translate.append(scoresListMap[i]['translate'])
        #     writing.append(scoresListMap[i]['writing'])
        #     details.append(scoresListMap[i]['details'])
        #     subjective_qz.append(scoresListMap[i]['subjective_qz'])
        #     objective_qm.append(scoresListMap[i]['objective_qm'])
        #     subjective_qm.append(scoresListMap[i]['subjective_qm'])
        #     xuewei.append(scoresListMap[i]['xuewei'])
        #
        # vocabulary = round(gainRate_ent(vocabulary, xuewei), 6)
        # hearing = round(gainRate_ent(hearing, xuewei), 6)
        # translate = round(gainRate_ent(translate, xuewei), 6)
        # writing = round(gainRate_ent(writing, xuewei), 6)
        # details = round(gainRate_ent(details, xuewei), 6)
        # subjective_qz = round(gainRate_ent(subjective_qz, xuewei), 6)
        # objective_qm = round(gainRate_ent(objective_qm, xuewei), 6)
        # subjective_qm = round(gainRate_ent(subjective_qm, xuewei), 6)

        # resultMap = {
        #     'vocabulary': vocabulary,
        #     'hearing': hearing,
        #     'translate': translate,
        #     'writing': writing,
        #     'details': details,
        #     'subjective_qz': subjective_qz,
        #     'objective_qm': objective_qm,
        #     'subjective_qm': subjective_qm
        # }
        # resultMap = {
        #     '单词': vocabulary,
        #     '听力': hearing,
        #     '翻译': translate,
        #     '写作': writing,
        #     '细节': details,
        #     '期中': subjective_qz,
        #     '期末客观': objective_qm,
        #     '期末主观': subjective_qm,
        #     'Test1': 0.21
        # }
        # print('resultMap=', resultMap)
        # 如果没有结果返回
        # if len(scoresListMap) == 0:
        #     # #########具体应该是什么code_number、返回什么错误信息需要修改#########
        #     code_number = 4000
        #     return JsonResponse({'code': code_number, 'message': status_code[code_number]}, safe=False)
        # if len(list(resultMap.keys())) <= 0:
        #     resultMap['示例'] = 0.54

        code_number = '2000'

        # 返回结果
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': resultMap,
        }
        # print(result)
        return JsonResponse(result, safe=False)
