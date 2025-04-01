from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('download/', views.download_zip, name='download_zip'),
]
