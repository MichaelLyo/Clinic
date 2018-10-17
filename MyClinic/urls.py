from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transform_validity',views.transform_validity,name= 'transform_validity')
]