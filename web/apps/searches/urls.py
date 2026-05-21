from django.urls import path

from . import views

app_name = "searches"

urlpatterns = [
    path("", views.search_list, name="list"),
    path("nova/", views.search_new, name="new"),
    path("<int:pk>/", views.search_detail, name="detail"),
    path("<int:pk>/progresso/", views.search_progress, name="progress"),
    path("<int:pk>/cancelar/", views.search_cancel, name="cancel"),
]
