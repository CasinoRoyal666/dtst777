from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('list/', views.list_view, name='list')
]