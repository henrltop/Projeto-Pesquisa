from django.urls import path

from . import views

app_name = "validations"

urlpatterns = [
    path("", views.config_view, name="config"),
    path("sessao/<int:session_id>/", views.review_view, name="review"),
    path("sessao/<int:session_id>/resultado/", views.result_view, name="result"),
    path("sessao/<int:session_id>/exportar/", views.export_csv, name="export"),
]
