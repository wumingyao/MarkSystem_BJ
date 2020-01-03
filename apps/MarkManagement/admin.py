#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to register the models.

http://localhost:8000/admin could see these models.
"""

from django.contrib import admin
from apps.MarkManagement.model.models import Teacher
from .model import models

admin.site.register(models.Teacher)
admin.site.register(models.University)
admin.site.register(models.Token)
admin.site.register(models.TitleGroup)
admin.site.register(models.Title)
admin.site.register(models.Lesson)
admin.site.register(models.Major)
admin.site.register(models.College)
admin.site.register(models.Point)
admin.site.register(models.Student)
admin.site.register(models.Class)
admin.site.register(models.ClassInfo)
