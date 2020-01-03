from apps.MarkManagement.view.common import *
import pandas as pd
import numpy as np

class ComparisonClass(viewsets.ViewSet):
    def comparison(self, request):
        # lessonId = request.GET.get('lesson_id')
        # classInfo_ids = request.GET.get('classInfo_ids').split(',')
        # titleGroups = request.GET.get('titleGroup_names').split(',')
        # print(request)
        lessonId = request.data.get('lesson_id')
        classInfo_ids = request.data.get('classInfo_ids')
        titleGroups = request.data.get('titleGroup_names')

        points = [] # points中每个元素对应一个班的数据
        for id in classInfo_ids:
            points.append(list(TotalPoint.objects.filter(lessonId=lessonId, classInfo_id=int(id), titleGroup__in=titleGroups).values()))

        classes = []
        weight = {} #大项权重
        w = list(TitleGroup.objects.filter(lesson_id=lessonId,name__in=titleGroups).values())
        for i in w:
            weight.update({i['name']: i['weight']})

        for p in range(len(points)):
            final_scores = [] # 一个班中所有学生的所选成绩
            data = pd.DataFrame(points[p])
            if not points[p]:
                continue
            w = []
            for id in set(data['stu_id']): #遍历每个学生
                d = data[data.stu_id==id].groupby(['titleGroup']).sum()
                groups = list(d.index)
                if len(w) == 0:
                    for g in groups:
                        w.append(weight[g])
                # print(len(d['final_score']))
                score = 0
                for i in range(len(d['final_score'])):
                    score += d['final_score'][i] # 大项乘以相对权重再相加
                final_scores.append(score)
            final_scores = np.array(final_scores)
            full_point = float(sum(w))
            final_scores = final_scores * 100 / full_point
            avgPoint = sum(final_scores)/len(final_scores)
            name = list(ClassInfo.objects.filter(id=classInfo_ids[p]).values())[0]['name']
            # print(final_scores)
            passRate = len(final_scores[final_scores >= 60])/len(final_scores) * 100
            below_60 = len(final_scores[final_scores < 60])
            below_70 = len(final_scores[final_scores < 70])
            below_80 = len(final_scores[final_scores < 80])
            below_90 = len(final_scores[final_scores < 90])
            below_100 = len(final_scores[final_scores <= 100])
            people = [below_60, below_70-below_60, below_80-below_70, below_90-below_80, below_100-below_90]
            classes.append({'weight': w, 'name': name, 'avgPoint': round(avgPoint, 2), 'passRate': round(passRate, 2), 'people': people,\
                            'max': round(max(final_scores)), 'min': round(min(final_scores)), "excellent": people[-1],})


        result = {
            'code': '2000',
            'data': classes,
        }
        return JsonResponse(result, safe=False)