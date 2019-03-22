from app.models import *
import csv
import random
from questions import questions

def initialize_projects():
    for proj in range(1,5):
        project, created = Project.objects.get_or_create(name=proj)
        project.save()

def initialize_student_project():
    with open('teams12.csv') as f:
        reader = csv.reader(f, delimiter=',')
        line_count = 0
        for row in reader:
            print(row)
            if line_count == 0:
                line_count += 1
            else:
                student_name, team_no = row
                student, created = Student.objects.get_or_create(name=student_name)
                student.save()
                print('student saved')
                # assuming project is already created
                for project_num in range (1,3):
                    project = Project.objects.get(name=project_num)
                    studentProject = StudentProject(team=team_no,student=student,project=project)
                    studentProject.save()
        print('done with teams 1,2')
    with open('teams34.csv') as g:
        reader = csv.reader(g, delimiter=',')
        line_count = 0
        for row in reader:
            print(row)
            if line_count == 0:
                line_count += 1
            else:
                student_name, team_no = row
                student, created = Student.objects.get_or_create(name=student_name)
                print('student retrieved')
                # assuming project is already created
                for project_num in range (3,5):
                    project = Project.objects.get(name=project_num)
                    studentProject = StudentProject(team=team_no,student=student,project=project)
                    studentProject.save()
        print('done with teams 3,4')

def initialize_evaluations():
    projects = Project.objects.all()
    for student in Student.objects.all():
        for proj in projects:
            team = StudentProject.objects.get(student=student, project=proj).team
            team_mates = StudentProject.objects.filter(team=team,project=proj)
            for entry in team_mates:
                Evaluation(project=proj,student_from=entry.student, student_to=student
                           ,status='incomplete',score=0)\
                    .save()
    print('saved evaluations')

def initialize_categories():
    for cat in questions.keys():
        category, created = Category.objects.get_or_create(name=cat)
        category.save()
        print("saved categories")

def initialize_questions():
    for cat, qs in questions.items():
        category = Category.objects.get(name=cat)
        for i in range(5):
            # first 5 open ended questions
            Question(text=qs[i],category=category,type='metric').save()
        Question(text= category.name + " Qualitative", category=category,type='comment').save()
        print("saved questions for", category)
    print('saved all questions')







