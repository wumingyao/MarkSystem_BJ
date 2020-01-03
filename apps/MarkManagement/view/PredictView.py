#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
    This file is for the performance prediction.
"""

from apps.MarkManagement.view.common import *
from pandas.core.frame import DataFrame
from keras.layers import Dense, Dropout
from keras.models import Sequential
from sklearn.externals.joblib import load
import keras
import time
import numpy as np


class PredictViewSet(viewsets.ViewSet):
    def predictScore(self, request):
        """
        预测学位英语成绩
        使用期中客观分、期中主观分、期中总分、期末客观分、期末主观分和期末总分来预测研究生学位英语成绩
        :param request:
        :return:
        """

        def getScoreListMapBySidList(id_list, classInfo_id):
            """
            该函数用于，根据sidList获得sidList中所包含的学生在该课程中的所有分数
            :param id_list: sidList是sid列表，形如['2019001','2019002',……]
            :return:result是一个ListMap,形如[map1,map2,……]，一个具体map格式如下
                    客观分, 主观分, 总分, 词汇, 听力, 翻译, 写作, 细节, 客观分m, 主观分m, 总分m, 总分1
            """

            point_set = Point.objects.filter(
                Q(student_id__in=id_list) & Q(classInfo_id=classInfo_id) & ~Q(title__titleGroup__name='出勤') & ~Q(
                    title__titleGroup__name='分组') & ~Q(title__titleGroup__name='加分')).order_by(
                'student_id', 'date')
            dataSet = []
            for id in id_list:
                pointNumbers = [point['pointNumber'] for point in
                                list(point_set.filter(student_id=id).values('pointNumber'))]
                if len(pointNumbers) <= 0:
                    pointNumbers = [0, 0, 0, 0]
                else:
                    if len(pointNumbers) >= 4:
                        pointNumbers = pointNumbers[-4:]
                    else:
                        for i in range(4 - len(pointNumbers)):
                            pointNumber = pointNumbers[-1]
                            pointNumbers.append(pointNumber)
                dataSet.append(pointNumbers)
            return np.array(dataSet)

        def getNameListBySidList(id_list):
            """
            根据sidList得到nameList
            :param id_list:
            :return:
            """

            student_set = Student.objects.filter(id__in=id_list)

            name_list = []
            sid_list = []

            for student in student_set:
                student_dict = model_to_dict(student)
                name_list.append(student_dict['name'])
                sid_list.append(student_dict['sid'])

            return sid_list, name_list

        # *********************v2_新增1_start *********************#
        # ann预测
        def annpredict(model_file, testData, inputdim):
            model = Sequential()
            model.add(Dense(16, kernel_initializer='normal', input_dim=inputdim, activation='relu'))
            model.add(Dense(32, kernel_initializer='normal', activation='relu'))
            model.add(Dropout(0.01))
            model.add(Dense(32, kernel_initializer='normal', activation='relu'))
            model.add(Dense(32, kernel_initializer='normal', activation='relu'))
            model.add(Dense(units=1))
            model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['accuracy'])
            # model.summary()
            model.load_weights(model_file)
            # model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['accuracy'])

            preds = model.predict(testData)
            keras.backend.clear_session()
            return preds

        # *********************v2_新增1_end *********************#

        # 获得要预测的学生的sidlist
        # 从前端读到数据
        idList = request.data['sidList']
        classInfo_id = request.data['classInfo_id']

        # 获得学生姓名列表
        sidList, nameList = getNameListBySidList(idList)

        dataset = getScoreListMapBySidList(idList, classInfo_id)

        # ann预测结果
        start = time.time()
        annpre = annpredict("./apps/static/model/Weights-001--12.99853.hdf5", dataset, 4)
        annpre = list(annpre.reshape((1, annpre.shape[0]))[0])
        # # 返回结果
        predictListMap = []
        #
        for i in range(len(idList)):
            pointNumber = int(annpre[i])+10
            if pointNumber >= 100:
                pointNumber = 100
            if pointNumber <= 0:
                pointNumber = 0
            if pointNumber < 60.0:
                ps = "0"
            else:
                ps = '1'
            mp = {
                'id': idList[i],
                'sid': sidList[i],
                'name': nameList[i],
                'pass': ps,
                'pointNumber': pointNumber,
            }
            predictListMap.append(mp)
        #     # ******************************预测部分结束******************************

        # 如果没有结果返回
        if len(predictListMap) == 0:
            # #########具体应该是什么code_number、返回什么错误信息需要修改#########
            code_number = 4000
            return JsonResponse({'code': code_number, 'message': status_code[code_number]}, safe=False)
        code_number = '2000'
        # 返回结果
        result = {
            'code': code_number,
            'message': status_code[code_number],
            'subjects': predictListMap,
            'count': len(predictListMap),
        }
        return JsonResponse(result, safe=False)
