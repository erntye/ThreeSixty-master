from django.contrib import admin
from .models import *

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)

class StudentProjectAdmin(admin.ModelAdmin):
    list_display = ('team', 'student', 'project')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'type')

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text','question', 'time_in', 'student_from', 'student_to', 'project')

class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('student_from','student_to', 'time_in','project', 'status', 'score')

admin.site.register(Student, StudentAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(StudentProject, StudentProjectAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Evaluation, EvaluationAdmin)