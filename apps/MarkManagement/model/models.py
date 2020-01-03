#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
This file is for the creation of mysql database.

Here are the classes and tables:
University: t_University(id, name, shortname)
   College: t_College   (id, name, shortname, university(FK))
   Teacher: t_Teacher   (id, tid, password, name, college(FK), is_manager, email, mobile)
     Token: t_Token     (id, token_text, teacher(FK), create_time)
     Major: t_Major     (id, name, shortname, college(FK))
   Student: t_Student   (id, sid, name, year, major(FK))
    Lesson: t_Lesson    (id, name, college(FK))
 ClassInfo: t_ClassInfo (id, name, teacher(FK), semester, week, room, cid, lesson(FK))
     Class: t_Class     (id, student(FK), classInfo(FK))
TitleGroup: t_TitleGroup(id, name, lesson(FK), weight)
     Title: t_Title     (id, name, titleGroup(FK), weight, classInfo(FK))
     Point: t_Point     (id, classInfo(FK), student(FK), title(FK), pointNumber, date, note)

warning insertMethod duplicated
warning model index not set
"""

from django.db import models


class University(models.Model):
    """
    学校
    t_University table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='学校名称', default='', unique=True)
    shortname = models.CharField(max_length=20, verbose_name='学校昵称', default='')

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 't_University'


class College(models.Model):
    """
    学院
    t_College table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default='')
    shortname = models.CharField(max_length=20, default='')
    university = models.ForeignKey(University, on_delete=models.SET_NULL, to_field='id', verbose_name='所在学校表主键',
                                   null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        unique_together = ("name", "shortname")
        db_table = 't_College'


class Teacher(models.Model):
    """
    教师(用户)
    t_Teacher table
    """
    id = models.AutoField(primary_key=True)
    tid = models.CharField(max_length=20, verbose_name='教师工号', default='', unique=True)
    password = models.CharField(max_length=128, verbose_name='密码', default='')
    name = models.CharField(max_length=20, verbose_name='用户姓名', default='')
    college = models.ForeignKey(College, on_delete=models.SET_NULL, to_field='id', verbose_name='所属学院id', null=True,
                                blank=True)
    is_manager = models.BooleanField(max_length=1, default=False, verbose_name='管理员')
    email = models.CharField(max_length=40, verbose_name='邮箱', default='')
    mobile = models.CharField(max_length=20, verbose_name='电话', default='')

    def __str__(self):
        return (str)(self.id) + '-' + self.name

    class Meta:
        managed = True
        db_table = 't_Teacher'


class Token(models.Model):
    """
    token验证模型
    t_Token table
    """
    id = models.AutoField(primary_key=True)
    token_text = models.CharField(max_length=128, verbose_name='token', default='')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, to_field='id', verbose_name='所属教师id', null=True,
                                blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return (str)(self.teacher.id) + '-' + self.teacher.name + '-' + self.token_text

    # destroy_time
    class Meta:
        managed = True
        db_table = 't_Token'


class Major(models.Model):
    """
    专业
    t_Major table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='专业名称', default='')
    shortname = models.CharField(max_length=10, verbose_name='专业昵称', default='')
    college = models.ForeignKey(College, on_delete=models.SET_NULL, to_field='id', null=True, blank=True,
                                verbose_name='所在学院id')

    def __str__(self):
        return self.college.name + '-' + self.name

    class Meta:
        managed = True
        unique_together = ("name", "college")
        db_table = 't_Major'


class Student(models.Model):
    """
    学生
    t_Student table
    """
    id = models.AutoField(primary_key=True)
    sid = models.CharField(max_length=20, verbose_name='学生学号', default='', unique=True)
    name = models.CharField(max_length=20, verbose_name='学生名', default='')
    year = models.CharField(max_length=6, verbose_name='学生学年', default='')
    majorName = models.CharField(max_length=20, verbose_name='专业名称', default='', null=True)
    collegeName = models.CharField(max_length=20, verbose_name='学院名称', default='', null=True)
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, to_field='id', verbose_name='专业id', null=True,
                              blank=True)

    def __str__(self):
        return (str)(self.sid) + '-' + self.name

    class Meta:
        managed = True
        db_table = 't_Student'


class Lesson(models.Model):
    """
    课程
    t_Lesson table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, verbose_name='课程名', default='')
    college = models.ForeignKey(College, on_delete=models.SET_NULL, to_field='id', verbose_name='学院id', null=True,
                                blank=True)

    def __str__(self):
        return self.college.name + '-' + self.name

    class Meta:
        managed = True
        unique_together = ('name', 'college')
        db_table = 't_Lesson'


class ClassInfo(models.Model):
    """
    班级信息模型
    t_ClassInfo table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, verbose_name='教学班信息', default='')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, to_field='id', verbose_name='教师表id', null=True,
                                blank=True)
    # year = models.CharField(max_length=6, verbose_name='开课年', default='')
    # month = models.CharField(max_length=2, verbose_name='开课月', default='')
    semester = models.CharField(max_length=20, verbose_name='学期', default='')
    # date = models.CharField(max_length=200, verbose_name='开课时间', default='')
    week = models.CharField(max_length=20, verbose_name='开课时间', default='')
    room = models.CharField(max_length=200, verbose_name='教室', default='')
    cid = models.CharField(max_length=40, verbose_name='课程代号', default='')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, to_field='id', verbose_name='所属课程组id', null=True,
                               blank=True)

    def __str__(self):
        return self.semester + '-' + self.teacher.name + '-' + self.lesson.name + '-' + self.name

    class Meta:
        managed = True
        db_table = 't_ClassInfo'


class Class(models.Model):
    """
    班级映射模型
    t_Class table
    """
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, to_field='id', verbose_name='学生id', null=True,
                                blank=True)
    # sid = models.CharField(max_length=20, verbose_name='学号', default='',  )
    # sname = models.CharField(max_length=20, verbose_name='学生姓名', default='',  )
    # index = models.CharField(max_length=16, verbose_name='学生班内序号', default='',  )
    classInfo = models.ForeignKey(ClassInfo, on_delete=models.SET_NULL, to_field='id', verbose_name='课程详细id', null=True,
                                  blank=True)

    def __str__(self):
        return self.classInfo.name + '-' + self.student.name

    class Meta:
        managed = True
        unique_together = ('student', 'classInfo')
        db_table = 't_Class'


class TitleGroup(models.Model):
    """
    分数组成大项
    t_TitleGroup table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='列的组名', default='')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, to_field='id', verbose_name='类别所属课程组id', null=True,
                               blank=True)
    weight = models.DecimalField(verbose_name='权重', default=0, max_digits=5, decimal_places=2)

    def __str__(self):
        return self.lesson.name + '-' + self.name + '-' + (str)(self.weight)

    class Meta:
        managed = True
        unique_together = ('name', 'lesson')
        db_table = 't_TitleGroup'


class Title(models.Model):
    """
    分数组成小项
    t_Title table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='列名', default='')
    titleGroup = models.ForeignKey(TitleGroup, on_delete=models.SET_NULL, to_field='id', verbose_name='列的组id',
                                   null=True, blank=True)
    weight = models.DecimalField(verbose_name='权重', default=0, max_digits=5, decimal_places=2)
    classInfo = models.ForeignKey(ClassInfo, on_delete=models.SET_NULL, to_field='id', verbose_name='列的教学班id',
                                  null=True, blank=True)

    def __str__(self):
        return self.classInfo.lesson.name + '-' + self.titleGroup.name + '-' + self.name + '-' + (str)(self.weight)

    class Meta:
        managed = True
        unique_together = ('titleGroup', 'name', 'classInfo')
        db_table = 't_Title'


class Point(models.Model):
    """
    分数
    t_Point table
    """
    id = models.AutoField(primary_key=True)
    classInfo = models.ForeignKey(ClassInfo, on_delete=models.SET_NULL, to_field='id', verbose_name='分数的课程的id',
                                  null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, to_field='id', verbose_name='分数的学生id', null=True,
                                blank=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, to_field='id', verbose_name='列id', null=True, blank=True)
    pointNumber = models.FloatField(verbose_name='分数', default=0)
    date = models.DateTimeField(verbose_name='时间戳', auto_now=True, null=True, blank=True)
    note = models.CharField(max_length=400, default='')

    def __str__(self):
        return self.classInfo.name + '-' + self.student.name + '-' + self.title.name + '-' + (str)(self.pointNumber)

    class Meta:
        managed = True
        unique_together = ('student', 'title')
        db_table = 't_Point'
