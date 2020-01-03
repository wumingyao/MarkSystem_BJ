#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is for the basic operation of users.

Here are operations:
                logon: POST http://localhost:8000/api/v1/user/logon
                login: POST http://localhost:8000/api/v1/user/login
               logout: POST http://localhost:8000/api/v1/user/logout
get_user_full_message: GET  http://localhost:8000/api/v1/user/info/display
                query: GET  http://localhost:8000/api/v1/user/info/format
      change_own_info: PUT http://localhost:8000/api/v1/usr/info/format
"""

from apps.MarkManagement.view.common import *


class TeacherViewSet(viewsets.ViewSet):

    def logon(self, request):
        """
        注册
        :param request: the request from browser. 用来获取注册信息
        :return: JSON response. 包括code, message
                1、如果必填注册信息有空，返回parameter_missed的JSON response
                2、如果注册教师已存在，返回状态码4023以及其对应的信息
                3、如果满足条件，尝试注册
                    注册失败，返回insert_failed的JSON response
                    注册成功，返回insert_succeed的JSON response
        """
        post_data = request.data
        tid = post_data.get('tid')
        password = post_data.get('password')
        college_id = post_data.get('college_id')
        name = post_data.get('name')
        email = post_data.get('email', '')
        mobile = post_data.get('mobile', '')

        if password is None or college_id is None or tid is None or name is None:
            return parameter_missed()
        # college_set = College.objects.filter(id=college_id)
        # if college_set.exists() == False:
        # return JsonResponse({'code': '1022', 'message': status_code['4032']}, safe=False)

        teacher_set = Teacher.objects.filter(Q(tid=tid))
        if teacher_set.exists():
            code_number = '4023'
            return JsonResponse({'code': code_number, 'message': status_code[code_number]}, safe=False)

        teacher = Teacher()
        teacher.tid = tid
        teacher.password = password
        teacher.college_id = college_id
        teacher.name = name
        teacher.mobile = mobile
        teacher.email = email

        try:
            teacher.save()
        except Exception as e:
            return insert_failed()

        return insert_succeed()

    def login(self, request):
        """
        登陆
        :param request: the request from browser. 用来获取登陆信息
        :return: JSON response. 包括code, message, subjects(opt)
                1、如果有参数为空，返回parameter_missed的JSON response
                2、如果符合条件，尝试查询
                    查询失败，登陆失败，数据库中没有用户信息，返回状态码4021以及对应的状态信息
                    查询成功，登陆成功，为用户创建token，用于之后操作的token验证，subjects为token和teacher的id，状态码2000
        """
        print("login")
        post_data = request.data
        tid = post_data.get('tid')
        password = post_data.get('password')
        if tid is None or password is None:
            return parameter_missed()

        teacher_set = Teacher.objects.filter(tid=tid, password=password)

        if teacher_set.exists():
            access_token = Token()
            access_token.teacher = teacher_set[0]
            access_token.token_text = create_md5(password)
            access_token.save()
            subjects = {
                'token': access_token.token_text,
                'id': access_token.teacher.id,
                'is_manager': access_token.teacher.is_manager
            }
            code_number = '2000'
            return JsonResponse(
                {'code': code_number,
                 'message': status_code[code_number],
                 'subjects': subjects}, safe=False)
        else:
            code_number = '4021'
            return JsonResponse({'code': code_number, 'message': status_code[code_number]}, safe=False)

    def logout(self, request):
        """
        登出
        :param request: the request from browser. 用来获取token
        :return: JSON response. 包括code, message
                1、登出之后，尝试删除token
                    删除失败，返回delete_failed的JSON response
                    删除成功，返回delete_succeed的JSON response
        """
        access_token = request.META.get("HTTP_TOKEN")
        if access_token:
            # 删除token
            try:
                Token.objects.filter(token_text=access_token).delete()
                return delete_succeed()
            except Exception as e:
                return delete_failed()
        return delete_failed()

    def query(self, request):
        """
        获取教师个人信息
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
        tid = request.GET.get('tid')
        name = request.GET.get('name')
        college_id = request.GET.get('college_id')
        email = request.GET.get('email')
        mobile = request.GET.get('mobile')
        is_manager = request.GET.get('is_manager')

        if id is None and name is None and tid is None and college_id is None and \
                email is None and mobile is None and is_manager is None:
            return parameter_missed()

        teacher_set = Teacher.objects.all()
        if id:
            teacher_set = teacher_set.filter(id=id)
        if tid:
            teacher_set = teacher_set.filter(tid=tid)
        if name:
            teacher_set = teacher_set.filter(name=name)
        if college_id:
            teacher_set = teacher_set.filter(college_id=college_id)
        if email:
            teacher_set = teacher_set.filter(email=email)
        if mobile:
            teacher_set = teacher_set.filter(mobile=mobile)
        if is_manager:
            teacher_set = teacher_set.filter(is_manager=is_manager)

        result = []

        teacher_set = teacher_set.values()
        for teacher in teacher_set:
            # 不返回用户密码
            del teacher['password']
            result.append(teacher)

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

    def get_user_full_message(self, request):
        """
        获取符合参数调节的已有教师详细信息（包括学校、学院信息）
        :param request: the request from browser.
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
        tid = request.GET.get('tid')
        name = request.GET.get('name')
        college_id = request.GET.get('college_id')
        email = request.GET.get('email')
        mobile = request.GET.get('mobile')
        is_manager = request.GET.get('is_manager')

        if id is None and name is None and tid is None and college_id is None and \
                email is None and mobile is None and is_manager is None:
            return parameter_missed()

        teacher_set = Teacher.objects.all()
        if id:
            teacher_set = teacher_set.filter(id=id)
        if tid:
            teacher_set = teacher_set.filter(tid=tid)
        if name:
            teacher_set = teacher_set.filter(name=name)
        if college_id:
            teacher_set = teacher_set.filter(college_id=college_id)
        if email:
            teacher_set = teacher_set.filter(email=email)
        if mobile:
            teacher_set = teacher_set.filter(mobile=mobile)
        if is_manager:
            teacher_set = teacher_set.filter(is_manager=is_manager)

        result = []
        for teacher in teacher_set:
            dict_teacher = model_to_dict(teacher)
            dict_college = model_to_dict(teacher.college)
            dict_university = model_to_dict(teacher.college.university)

            dict_teacher['college_id'] = dict_teacher['college']
            del dict_teacher['college']
            dict_teacher['college_message'] = dict_college

            dict_college['university_id'] = dict_college['university']
            del dict_college['university']
            dict_teacher['university_message'] = dict_university

            del dict_teacher['password']

            result.append(dict_teacher)

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

    def change_own_info(self, request):
        """
        更改教师个人信息
        :param request: the request from browser. 用来获取access_token和更新条件
        :return: JSON response. 包括code, message, subjects(opt)
                 1、如果token无效，即token不存在于数据库中，返回token_invalid的JSON response
                 2、如果request中的subjects参数为空，即Body-raw-json中没有内容，返回parameter_missed的JSON response
                 3、如果符合条件，尝试更新
                    更新失败，返回update_failed的JSON response
                    更新成功，返回update_succeed的JSON response
        """
        access_token = request.META.get("HTTP_TOKEN")
        if not token_verify(access_token):
            return token_invalid()

        subjects = request.data.get('subjects')

        if subjects is None:
            return parameter_missed()

        for subject_dict in subjects:
            id = subject_dict.get('id')
            tid = subject_dict.get('tid')
            name = subject_dict.get('name')
            college_id = subject_dict.get('college_id')
            mobile = subject_dict.get('mobile')
            email = subject_dict.get('email')
            old_password = subject_dict.get('old_password')
            new_password = subject_dict.get('new_password')
            if not id or not old_password:
                return parameter_missed()

            teacher_set = Teacher.objects.filter(id=id)

            for teacher in teacher_set:
                if teacher.password != old_password:
                    response = {
                        'code': '4021',
                        'message': status_code['4021']
                    }
                    return JsonResponse(response, safe=False)
                if tid:
                    teacher.tid = tid
                if name:
                    teacher.name = name
                if mobile:
                    teacher.mobile = mobile
                if email:
                    teacher.email = email
                if new_password:
                    teacher.password = new_password
                if college_id:
                    college_set = College.objects.filter(id=college_id)

                    if not college_set.exists():
                        continue

                    teacher.college = college_set[0]

                teacher.save()
                return update_succeed()

        return update_failed()
