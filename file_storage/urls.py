from django.urls import path

from . import views

urlpatterns = [
    # path('upload_image/', views.upload_image, name='upload_image'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('images/<int:image_id>/delete', views.delete_image, name='delete_image'),
    path('images/<int:image_id>/', views.view_image, name='view_image'),
    path('images/', views.images, name='images'),

    path('documents/', views.view_documents, name='documents'),
    path('confidential/', views.view_confidential, name='confidential'),
]