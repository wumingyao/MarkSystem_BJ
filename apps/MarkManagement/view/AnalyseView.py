#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is for the data analysis of student's scores
               AnalysisFun: The main analyse function.
                            POSTpip http://localhost:8000/api/v1/analysis
            AnalyseViewSet: According student's id list to get the student's name
                            GET http://localhost:8000/api/v1/analysis/student/name
  getScoreListMapBySidList: According student's id list to get a map including
                            学号，期中客观分，期中主观分，期中总分，期末客观分，期末主观分，期末总分
                            GET http://localhost:8000/api/v1/analysis/score/format
              getAllScores: According semester to get a map including
                            期中词汇分，期中听力分，期中翻译分，期中写作分，期中细节分，期中主观分，期末客观分，期末主观分，学位总分
                            GET http://localhost:8000/api/v1/analysis/score/all
"""
from __future__ import division

from django.shortcuts import render
from apps.MarkManagement.view.common import *
from django.forms.models import model_to_dict


class AnalyseViewSet(viewsets.ViewSet):

    def getNameListBySidList(self, request):
        """
        根据sidList得到nameList
        :param request: the request from browser.
        :return: the nameList
        """

        id_list = request.data.get('idList')

        if not id_list:
            return parameter_missed()

        student_set = Student.objects.filter(id__in=id_list)
        # student_set = student_set.values()

        name_list = []

        for student in student_set:
            student_dict = model_to_dict(student)
            del student_dict['sid']
            del student_dict['year']
            del student_dict['major']
            name_list.append(student_dict['name'])

        return JsonResponse(name_list, safe=False)

    def getScoreListMapBySidList(self, request):
        """
        根据sidList得到ListMap，Map的具体形式如下：
          map={
          'sid':'2019001',      //学号
          'score_zk':70,        //期中客观分
          'score_zz':18,        //期中主观分
          'score_zs':88,        //期中总分
          'score_mk':47,        //期末客观分
          'score_mz':10,        //期末主观分
          'score_ms':57,        //期末总分
          'vocabulary':20,      //期中客观单词分
          'hearing': 10,         //期中客观听力分
          'translate': 10,      //期中客观翻译分
          'writing': 10,        //期中客观写作分
          'details': 10,         //期中客观细节分
          }
        :param request: the request from browser.
        :return: the list map
        """

        id_list = request.data.get('idList')

        if not id_list:
            return parameter_missed()

        point_set = Point.objects.filter(student_id__in=id_list) \
            .values('pointNumber', 'student__sid', 'title__name', 'title__titleGroup__name')

        print('length of point_set=', len(point_set))

        temps = []
        dicts = {}
        results = []

        for point in point_set:
            point['sid'] = point['student__sid']
            if point['title__titleGroup__name'] == '期中客观分':
                point['score_zk'] = point['pointNumber']
                if point['title__name'] == '期中词汇':
                    point['vocabulary'] = point['pointNumber']
                if point['title__name'] == '期中听力':
                    point['hearing'] = point['pointNumber']
                if point['title__name'] == '期中翻译':
                    point['translate'] = point['pointNumber']
                if point['title__name'] == '期中写作':
                    point['writing'] = point['pointNumber']
                if point['title__name'] == '期中细节':
                    point['details'] = point['pointNumber']
            if point['title__titleGroup__name'] == '期中主观分':
                point['score_zs'] = point['pointNumber']
                point['score_zz'] = point['pointNumber']
            if point['title__titleGroup__name'] == '期末客观分':
                point['score_ms'] = point['pointNumber']
                point['score_mk'] = point['pointNumber']
            if point['title__titleGroup__name'] == '期末主观分':
                point['score_ms'] = point['pointNumber']
                point['score_mz'] = point['pointNumber']

            del point['pointNumber']
            del point['student__sid']
            del point['title__name']
            del point['title__titleGroup__name']
            temps.append(point)

        for temp in temps:
            if temp['sid'] in dicts:
                if 'score_zk' in dicts[temp['sid']] and 'score_zk' in temp:
                    dicts[temp['sid']]['score_zk'] += temp['score_zk']
                    del temp['score_zk']
                elif 'score_zs' in dicts[temp['sid']] and 'score_zs' in temp:
                    dicts[temp['sid']]['score_zs'] += temp['score_zs']
                    del temp['score_zs']
                elif 'score_ms' in dicts[temp['sid']] and 'score_ms' in temp:
                    dicts[temp['sid']]['score_ms'] += temp['score_ms']
                    del temp['score_ms']
                dicts[temp['sid']].update(temp)
            else:
                dicts[temp['sid']] = temp

        for value in dicts.values():
            if value != {}:
                if 'score_zk' not in value:
                    value['score_zk'] = 0
                if 'score_zz' not in value:
                    value['score_zz'] = 0
                if 'score_zs' not in value:
                    value['score_zs'] = 0
                if 'score_mk' not in value:
                    value['score_mk'] = 0
                if 'score_mz' not in value:
                    value['score_mz'] = 0
                if 'score_ms' not in value:
                    value['score_ms'] = 0
                if 'vocabulary' not in value:
                    value['vocabulary'] = 0
                if 'hearing' not in value:
                    value['hearing'] = 0
                if 'translate' not in value:
                    value['translate'] = 0
                if 'writing' not in value:
                    value['writing'] = 0
                if 'details' not in value:
                    value['details'] = 0

                results.append(value)

        return JsonResponse(results, safe=False)

    def getAllScores(self, request):
        """
        获取某学期内所有学生的成绩，得到一个listMap，Map的具体形式如下：
        map={
            'vocabulary':40,        //期中词汇分
            'hearing':9,            //期中听力分
            'translate':7,          //期中翻译分
            'writing':7,            //期中写作分
            'details':7,            //期中细节分
            'subjective_qz':20,     //期中主观分
            'objective_qm':60,      //期末客观分
            'subjective_qm':20,     //期末主观分
            'xuewei':70             //学位总分
        }
        :param request: the server from browser
        :return: the list map
        """

        semester = request.GET.get('semester')

        if not semester:
            return parameter_missed()

        temps = []
        dicts = {}
        results = []

        # improve the performance
        point_set = Point.objects.filter(classInfo__semester=semester) \
            .values('student', 'pointNumber', 'title__name', 'title__titleGroup__name')

        print('point_set length=', len(point_set))

        for point in point_set:
            if point['title__titleGroup__name'] == '期中客观分':
                if point['title__name'] == '期中词汇':
                    point['vocabulary'] = point['pointNumber']
                if point['title__name'] == '期中听力':
                    point['hearing'] = point['pointNumber']
                if point['title__name'] == '期中翻译':
                    point['translate'] = point['pointNumber']
                if point['title__name'] == '期中写作':
                    point['writing'] = point['pointNumber']
                if point['title__name'] == '期中细节':
                    point['details'] = point['pointNumber']
            if point['title__titleGroup__name'] == '期中主观分':
                point['subjective_qz'] = point['pointNumber']
            if point['title__titleGroup__name'] == '期末客观分':
                point['objective_qm'] = point['pointNumber']
            if point['title__titleGroup__name'] == '期末主观分':
                point['subjective_qm'] = point['pointNumber']

            elif point['title__titleGroup__name'] in ['学位主观分', '学位客观分']:
                point['xuewei'] = point['pointNumber']

            del point['pointNumber']
            del point['title__titleGroup__name']
            del point['title__name']
            temps.append(point)

        for temp in temps:
            if temp['student'] in dicts:
                if 'xuewei' in dicts[temp['student']] and 'xuewei' in temp:
                    dicts[temp['student']]['xuewei'] += temp['xuewei']
                else:
                    dicts[temp['student']].update(temp)
            else:
                dicts[temp['student']] = temp

        for value in dicts.values():
            if value != {}:
                if 'vocabulary' not in value:
                    value['vocabulary'] = 0
                if 'hearing' not in value:
                    value['hearing'] = 0
                if 'translate' not in value:
                    value['translate'] = 0
                if 'writing' not in value:
                    value['writing'] = 0
                if 'details' not in value:
                    value['details'] = 0
                if 'subjective_qz' not in value:
                    value['subjective_qz'] = 0
                if 'objective_qm' not in value:
                    value['objective_qm'] = 0
                if 'subjective_qm' not in value:
                    value['subjective_qm'] = 0
                if 'xuewei' not in value:
                    value['xuewei'] = 0

                results.append(value)

        for result in results:
            del result['student']

        return JsonResponse(results, safe=False)
