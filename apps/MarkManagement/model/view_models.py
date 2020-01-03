from .models import *

class TotalPoint(models.Model):
    id = models.AutoField(primary_key=True)
    stu_id = models.CharField(max_length=11)
    title = models.CharField(max_length=20)
    titleGroup = models.CharField(max_length=20)
    title_point = models.DecimalField(max_digits=5, decimal_places=2)
    titleWeight = models.DecimalField(max_digits=5, decimal_places=2)
    realTitle_point = models.DecimalField(max_digits=5, decimal_places=2)
    groupWeight = models.DecimalField(max_digits=5, decimal_places=2)
    lessonId = models.CharField(max_length=11)
    classInfo_id = models.CharField(max_length=11)
    final_score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'view_statics'

