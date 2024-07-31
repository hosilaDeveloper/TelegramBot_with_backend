from django.urls import path
from .views import TodoView, TodoDetail

urlpatterns = [
    path('todos/', TodoView.as_view(), name='todo-list'),
    path('todos/<int:pk>/', TodoDetail.as_view(), name='todo-detail')
]
