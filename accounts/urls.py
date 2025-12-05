from django.urls import path

from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/create/', views.UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user-edit'),
    path('users/<int:pk>/deactivate/', views.UserDeactivateView.as_view(), name='user-deactivate'),
]


