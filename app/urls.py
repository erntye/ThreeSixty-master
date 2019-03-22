from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='login'),
    path('profile', views.profile),
    path('projects', views.project),
    path('team', views.team),
    path('evaluation', views.evaluation),
    path('report', views.report),
    path('error', views.mismatch),
    path('accounts/login/', views.index),
    path('report/export', views.export_csv,name='export'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

