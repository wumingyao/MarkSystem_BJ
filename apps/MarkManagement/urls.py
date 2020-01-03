#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to register the function's urls.

http 中 get 方法进入 query 函数， post 方法进入 insert 函数, put 方法进入update 函数， delete 方法进入 remove 函数
"""

from apps.MarkManagement.view import views
from django.urls import re_path

urlpath = [
    # table
    re_path(r'^table/lesson/format', views.LessonViewSet.as_view({'get': 'query',
                                                                  'post': 'insert',
                                                                  'put': 'update',
                                                                  'delete': 'remove'})),
    # class_field
    re_path(r'^table/class_field/wrapper', views.ClassViewSet.as_view({'get': 'query_wrapper'})),
    re_path(r'^table/class_field/format', views.ClassViewSet.as_view({'get': 'query',
                                                                      'post': 'insert',
                                                                      'delete': 'remove'})),

    # class_info
    re_path(r'^table/class_info/format', views.ClassInfoViewSet.as_view({'get': 'query',
                                                                         'post': 'insert',
                                                                         'put': 'update',
                                                                         'delete': 'remove'})),
    # necessary
    re_path(r'^table/class_info/detail/some', views.ClassInfoViewSet.as_view({'get': 'get_classInfo_full_message'})),
    re_path(r'^table/class_info/detail/all',
            views.ClassInfoViewSet.as_view({'get': 'get_classInfo_full_message_all'})),

    re_path(r'^table/class_info/lessonList',
            views.ClassInfoViewSet.as_view({'post': 'getLessonListByTeacherId'})),

    # teacher,目前等价于user
    # re_path(r'^teacher/info/format$', views.TeacherViewSet.as_view({'get': 'query',
    #                                                               'put': 'update'})),

    # user
    # necessary
    re_path(r'^user/info/display', views.TeacherViewSet.as_view({'get': 'get_user_full_message'})),

    re_path(r'^user/info/format', views.TeacherViewSet.as_view({'get': 'query',
                                                                'put': 'change_own_info'})),

    re_path(r'^user/logon', views.TeacherViewSet.as_view({'post': 'logon'})),
    re_path(r'^user/login', views.TeacherViewSet.as_view({'post': 'login'})),
    re_path(r'^user/logout', views.TeacherViewSet.as_view({'post': 'logout'})),

    # user_manage
    re_path(r'^user/info/manage', views.TeacherManageViewSet.as_view({'get': 'query',
                                                                      'post': 'insert',
                                                                      'put': 'update',
                                                                      'delete': 'remove'})),
    # student
    # necessary
    re_path(r'^student/fuzzyMatch', views.StudentViewSet.as_view({'get': 'get_student_match'})),
    re_path(r'^student/display', views.StudentViewSet.as_view({'get': 'get_student_list'})),

    re_path(r'^student/format', views.StudentViewSet.as_view({'get': 'query',
                                                              'post': 'insert',
                                                              'put': 'update',
                                                              'delete': 'remove'})),
    # university
    re_path(r'^university/format', views.UniversityViewSet.as_view({'get': 'query',
                                                                    'post': 'insert',
                                                                    'put': 'update',
                                                                    'delete': 'remove'})),

    # college
    re_path(r'^college/display', views.CollegeViewSet.as_view({'get': 'get_college_list'})),
    re_path(r'^college/format', views.CollegeViewSet.as_view({'get': 'query',
                                                              'post': 'insert',
                                                              'put': 'update',
                                                              'delete': 'remove'})),
    # major
    re_path(r'^major/format', views.MajorViewSet.as_view({'get': 'query',
                                                          'post': 'insert',
                                                          'put': 'update',
                                                          'delete': 'remove'})),

    # point
    re_path(r'^point/getWeightData',
            views.PointViewSet.as_view({'get': 'getWeightData'})),
    re_path(r'^point/output',
            views.PointViewSet.as_view({'get': 'output'})),
    re_path(r'^point/get_AllClass_TitleGroup_Avgpiont',
            views.PointViewSet.as_view({'get': 'get_AllClass_TitleGroup_Avgpiont'})),
    re_path(r'^point/get_Count_point', views.PointViewSet.as_view({'get': 'get_Count_point'})),
    re_path(r'^point/display', views.PointViewSet.as_view({'get': 'get_point_list'})),
    re_path(r'^point/format', views.PointViewSet.as_view({'get': 'query',
                                                          'post': 'insert',
                                                          'put': 'update',
                                                          'delete': 'remove'})),
    re_path(r'^point/import_data', views.ImportDataViewSet.as_view({'post': 'insert'})),

    # title
    re_path(r'^title/display', views.TitleViewSet.as_view({'get': 'get_title_list'})),
    re_path(r'^title/format', views.TitleViewSet.as_view({'get': 'query',
                                                          'post': 'insert',
                                                          'put': 'update',
                                                          'delete': 'remove'})),
    # title_group
    re_path(r'^title_group/format', views.TitleGroupViewSet.as_view({'get': 'query',
                                                                     'post': 'insert',
                                                                     'put': 'update',
                                                                     'delete': 'remove'})),

    # TODO: semester change
    # re_path(r'^semester/$',views.)

    # analysis
    # re_path(r'^analysis/prediction', views.AnalysisViewSet.as_view({'post': 'AnalysisFun'})),
    re_path(r'^analysis/student/name', views.AnalyseViewSet.as_view({'post': 'getNameListBySidList'})),
    re_path(r'^analysis/score/format', views.AnalyseViewSet.as_view({'post': 'getScoreListMapBySidList'})),
    re_path(r'^analysis/score/all', views.AnalyseViewSet.as_view({'get': 'getAllScores'})),

    # 成绩预测
    re_path(r'^analysis/pass', views.PredictViewSet.as_view({'post': 'predictScore'})),

    # 课程分析
    re_path(r'^analysis/class', views.AnalysisViewSet.as_view({'post': 'Analysisfun'})),

    # 班级比较
    re_path(r'^point/comparison', views.ComparisonClass.as_view({'post': 'comparison'})),
]
