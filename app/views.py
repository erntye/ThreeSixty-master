import os
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from app.models import *
from datetime import datetime
import json, time
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import csv
from collections import OrderedDict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")

TA = [
    'awillerman@berkeley.edu',
    'gwynevere.hunger@berkeley.edu'
]


def index(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'login.html', context)
    else:
        full_name = request.POST.get('full_name', None)
        first_name = request.POST.get('given_name', None).split()[0]
        last_name = request.POST.get('family_name', None).split()[0]
        print(first_name,last_name)
        try:
            student = Student.objects.filter(name__icontains = first_name).filter(name__icontains = last_name)[0]
            update_student_data(student, dict(request.POST.lists()))
            student = Student.objects.filter(name__icontains = first_name).filter(name__icontains = last_name)[0] #with updated info
            request.session['student_name'] = student.name
            request.session['student_image_url'] = student.image_url
            request.session['student_email'] = student.email
            request.session['student_id'] = student.id

            #Add the user as a Django User
            user = User.objects.filter(username=student.email)
            if not user:
                password = 'WagwanObama'
                new_user = User.objects.create_user(username=student.email, password=password, email=student.email)
                new_user.save()

            result = authenticate(username=student.email, password='WagwanObama')
            if result is not None:
                login(request, result)

            return HttpResponse("success")
        except Exception as e:
            return HttpResponse(str(e) + " " + str(full_name))

def mismatch(request):
    context = {}
    return render(request, 'mismatch.html', context)

@login_required
def project(request):
    context = {}
    if request.session.get('student_email') in TA:
        HttpResponseRedirect('/report')
    context['student_image_url'] = request.session.get('student_image_url')
    context['student_name'] = request.session.get('student_name')
    context['student_id'] = request.session.get('student_id')
    return render(request, 'projects.html', context)

@login_required
def team(request):
    context = {}
    project_name = request.GET.get('project', None)
    current_student = Student.objects.get(id = request.session.get('student_id'))
    context['student_image_url'] = request.session.get('student_image_url')
    context['student_name'] = request.session.get('student_name')
    context['student_id'] = request.session.get('student_id')

    team_name = StudentProject.objects.get(student=current_student, project__name=project_name).team
    students = []
    if team_name and project_name:
        records = StudentProject.objects.filter(project__name = project_name, team=team_name)
        for record in records:
            evaluated = Evaluation.objects.filter(project__name=project_name, student_from=current_student, student_to=record.student, status='complete')
            if evaluated: evaluated = True
            else: evaluated = False
            students.append({'name': record.student.name, 'id': record.student.id, 'evaluated': evaluated, 'image_url': record.student.image_url})
    context['students'] = students
    context['project'] = project_name
    return render(request, 'team.html', context)

@login_required
def profile(request):
    context = {}
    student_id = request.GET.get('student')
    context['student'] = Student.objects.get(id = student_id)

    comments = Answer.objects.filter(question__type='comment').order_by('-id')
    context['comments'] = comments

    projects = Project.objects.all()
    context['categories'] = get_metrics_per_category_per_project(student_id, Category.objects.all(), projects)
    context['overall_score'], context['self_score']  = get_total_score(student_id)
    context['progress'] = get_progress_per_project(student_id, projects)

    return render(request, 'profile.html', context)

@login_required
def evaluation(request):
    context = {}
    if request.method == 'GET':
        student_id = request.GET.get('student', None)
        project= request.GET.get('project', 0)
        student = Student.objects.get(  id= student_id)
        student_project = StudentProject.objects.get(student=student,project__name=project)
        team = student_project.team
        context['student'] = student
        context['team'] = team
        context['project'] = project

        evaluation_questions = []
        categories= Category.objects.all()
        for category in categories:
            cat_questions = []
            questions = Question.objects.filter(category_id=category.id, type='metric')
            for question in questions:
                text = question.text.lower().replace("this person", student.name.split(' ')[0])
                text = text[0].upper() + text[1:]
                cat_questions.append({'text': text, 'id': question.id})
            evaluation_questions.append({'id': category.id, 'name': category.name, 'questions': cat_questions})
        context['evaluation_questions'] = evaluation_questions
        return render(request, 'evaluation.html', context)
    else:
        student = request.POST.get('student')
        project = request.POST.get('project')
        project = Project.objects.get(name=project)
        student_to = Student.objects.get(id = student)
        student_from = Student.objects.get(id = request.session.get('student_id')) # to be replaced with sessions

        questions = Question.objects.all()
        score = 0
        metric_counter = 0
        for question in questions:
            if question.type == 'metric':
                text = request.POST.get('qid_' + str(question.id), None)
                if text: score += int(text)
                metric_counter += 1
            else:
                text = request.POST.get('comment_' + str(question.category.id), None)
            if text:
                a = Answer(text = text, question=question, time_in = datetime.now(), project = project, student_from=student_from, student_to=student_to, category=question.category)
                a.save()

        #mark evaluation complete
        score = int((score / (metric_counter * 5)) * 100)
        e = Evaluation.objects.filter(project=project, student_from=student_from, student_to=student_to)
        if e:
            e = e[0]
            e.time_in=datetime.now()
            e.status='complete'
            e.score=score
            e.save()
        return HttpResponse(json.dumps({'success': True}))

@login_required
def report(request):
    context = {}
    students = Student.objects.all()
    context['records'] = students
    projects = Project.objects.all()
    score_dict = OrderedDict()
    for student in students:
        overall_score = 0
        scores = OrderedDict()
        for project in projects:
            # get avg score of a student for a particular project from all group mates
            evals = Evaluation.objects.filter(student_to=student, status='complete',project=project)\
                .exclude(student_from=student)
            # add avg score if project is already defined
            if evals:
                project_avg_score = round(evals.aggregate(Avg('score'))['score__avg'],2)
                scores[project] = project_avg_score
                overall_score += project_avg_score
            else: scores[project] = '-'
        # get avg score for all projects
        scores['overall'] = round(overall_score/len(projects),2)
        # sort to put overall first
        order = ['overall'] + list(projects)
        ordered_scores = OrderedDict((k,scores[k]) for k in order)
        score_dict[student] = ordered_scores
    context['score_dict'] = score_dict
    return render(request, 'report.html', context)

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="team evaluation scores.csv"'
    writer = csv.writer(response)
    header = "Student, Overall Score, Project 1 Score, Project 2 Score, Project 3 Score, Project 4 Score"
    writer.writerow(header.split(","))
    students = Student.objects.all()
    projects = Project.objects.all()
    for student in students:
        overall_score = 0
        row = ",{}".format(student.name)
        temp_row = ""
        for project in projects:
            # get avg score of a student for a particular project from all group mates
            evals = Evaluation.objects.filter(student_to=student, status='complete',project=project)\
                .exclude(student_from=student)
            # add avg score if project is already defined
            if evals:
                project_avg_score = round(evals.aggregate(Avg('score'))['score__avg'],2)
                temp_row +=",{}".format(project_avg_score)
                overall_score += project_avg_score
            else: temp_row += ", -"
        # get avg score for all projects
        row += ", {}".format(round(overall_score/len(projects),2)) + temp_row
        writer.writerow(row.split(","))
    return response


def update_student_data(student, data):
    student.email = data['email'][0]
    student.full_name = data['full_name'][0]
    student.given_name = data['given_name'][0]
    student.family_name = data['family_name'][0]
    student.image_url = data['image_url'][0]
    student.save()
    return True

def get_metrics_per_category_per_project(student_id, categories, projects):
    output = []
    for category in categories:
        arr = []
        for project in projects:
            a = Answer.objects.filter(student_to_id = student_id, category = category, project = project, question__type='metric').exclude(student_from_id=student_id)
            c = a.count()
            a = a.aggregate(Sum('text'))
            s = a['text__sum'] if a['text__sum'] else 0
            score = 0 if c ==0  else int(s / (c * 5) * 100)
            arr.append(score)
        output.append({'name': category.name, 'data': arr})
    return output

def get_total_score(student_id):
    total_score = Evaluation.objects.filter(student_to=student_id, status='complete').exclude(student_from_id=student_id).aggregate(Avg('score'))
    total_score = int(total_score['score__avg']) if total_score['score__avg'] else 0

    self_score = Evaluation.objects.filter(student_to=student_id, student_from_id=student_id, status='complete').aggregate(Sum('score'))
    self_score = self_score['score__sum'] if self_score['score__sum'] else 0
    return total_score, self_score

def get_progress_per_project(student_id, projects):
    output = []
    for project in projects:
        i = Evaluation.objects.filter(student_to=student_id, project=project, status='complete').count()
        output.append(i)
    return output

### to get a csv file if needed
# def generate_instructor_csv():
#     with open('team_evaluation_scores.csv','w',newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         header = "Student, Overall Score, Project 1 Score, Project 2 Score, Project 3 Score, Project 4 Score"
#         writer.writerow(header.split(","))
#         students = Student.objects.all()
#         projects = Project.objects.all()
#         for student in students:
#             overall_score = 0
#             row = f"{student.name}"
#             temp_row = ""
#             for project in projects:
#                 # get avg score of a student for a particular project from all group mates
#                 evals = Evaluation.objects.filter(student_to=student, status='complete',project=project)\
#                     .exclude(student_from=student)
#                 # add avg score if project is already defined
#                 if evals:
#                     project_avg_score = round(evals.aggregate(Avg('score'))['score__avg'],2)
#                     temp_row += f", {project_avg_score}"
#                     overall_score += project_avg_score
#                 else: temp_row += ", -"
#             # get avg score for all projects
#             row += f", {round(overall_score/len(projects),2)}" + temp_row
#             writer.writerow(row.split(","))



