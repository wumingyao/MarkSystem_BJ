## requirements.txt:django工程需要的包
## APIDoucument.html：接口文档说明(有部分接口具体看代码）
## DatabaseDesigning.pdf:数据库设计说明(数据库具体看1106.sql)

### V_1.0.1版本：
* 修改日期 2019/09/29
* 1、LessonView。py
* 增加课程的时候，增加初始大项['平时', '出勤', '期中', '期末', '加分'],加分和出勤初始权重为0，平时',期中, 期末，初始权重分别是33.33
* 小项权重改为占比=100/n ,n为该大项对应有n个小项

### V_1.0.2版本：
* 1、更改table/class_info/format_get接口，增加课程人数属性
* 2、更改title/format_post接口，添加小项的时候，判断其归属大项设置默认初始值
* 3、更改point/display接口，提高性能
* 4、table/class_info/format 修改学期匹配bug

### V_1.0.3版本：
* updateDate:2019/11/07
* 1、增加point/get_Count_point接口
* 接口说明：前端传来 classinfo_id 和title_id 返回一个数组，里面包含0-60 60-70 70-80 80-90 90-100 的人数

### V_1.0.4版本
* 修改/point/format/get接口：为每个point增加titleGroupName字段
* 增加point/get_AllClass_TitleGroup_Avgpiont/get接口：根据lesson_id返回所有班级所有大项的平均分

### V_1.0.5版本
* 修改table/class_info/detail/some接口bug
* classInfo对应teacher为空的情况

### V_1.0.6版本 20191121
* 1 修改加分项初始值为空
* 2 修改课程分析bug
* 3 优化point/format/接口性能
* 4 训练成绩预测模型，实现动态预测

### V_1.1.0 20191204
* 1 修改数据库student加两字段majorName和collegeName，Point中的note的长度变为400
**   python manage.py makemigrations AppTest(个人App文件名)
**   python manage.py migrate
* 2 修改StudentView中所有接口
* 3 修改大项权重不能为0的bug
* 4 解决大项权重精度损失问题
* 5 初始化增加分组大项

### 程远恒版本
* 新增了测试文件Analyze.py, 修改了urls.py中的最后一项
* 新增viewmodels.py 并修改view/common.py 和views.py
* 新增conparison.py 视图

### V_1.1.1 20191209
* 1 增加模糊匹配接口

### V_1.1.3 20191231
* 1 增加成绩分析接口
* 2 增加成绩导出接口
