from django.urls import path
from order import views

urlpatterns = [
    path('', views.orders_list, name='orders_list'),
    path('my/', views.my_orders, name='my_orders'),
    path('create/', views.create_order, name='create_order'),
    path('close/<int:order_id>/', views.close_order, name='close_order'),
]