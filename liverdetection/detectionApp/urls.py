from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('edit_page/<str:image_name>/', views.edit_page, name='edit_page')
]
