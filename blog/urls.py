from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('<int:year>/<int:month>/<slug:slug>/', views.blog_post, name='blog_post'),
]