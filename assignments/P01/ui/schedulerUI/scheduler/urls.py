from django.urls import path

from . import views


urlpatterns = [
    # path("", views.index, name="index"),
    path("", views.get_data, name=""),
    path("add_process",views.add_process,name="add_process"),
    path('add_process_bulk', views.add_process_bulk, name='add_process_bulk'),
]