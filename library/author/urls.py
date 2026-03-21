from django.urls import path
from author import views

urlpatterns = [
    path('', views.authors_list, name='authors_list'),
    path('create/', views.author_create, name='author_create'),
    path('delete/<int:author_id>/', views.author_delete, name='author_delete'),
]