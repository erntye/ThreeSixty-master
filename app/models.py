from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=100, null=True)
    given_name = models.CharField(max_length=100, null=True)
    family_name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    image_url = models.CharField(max_length=300, null=True)

    def __str__(self):
        return str(self.name)


class Project(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class StudentProject(models.Model):
    team = models.CharField(max_length=200)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class Question(models.Model):
    text = models.TextField()
    type = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.text)


class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    student_from = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, related_name="answer_student_from")
    student_to = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, related_name="answer_student_to")
    time_in = models.DateTimeField(auto_now_add=True, null=True)


class Evaluation(models.Model):
    text = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    student_from = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, related_name="Student_from")
    student_to = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, related_name="Student_to")
    time_in = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
