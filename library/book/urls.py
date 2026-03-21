from django.urls import path
from . import views

app_name = 'book'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('add/', views.add_book, name='add_book'),
    path('<int:book_id>/', views.book_detail, name='book_detail'),
    path('user/<int:user_id>/', views.books_by_user, name='books_by_user'),
]