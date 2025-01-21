from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('edit_page/<str:image_name>/', views.edit_page, name='edit_page'),
    path('training', views.training, name='training'),

    path('delete_file', views.delete_file, name='delete_file'),
    path('download/<str:folder_name>/', views.download_folder, name='download_folder')
]
