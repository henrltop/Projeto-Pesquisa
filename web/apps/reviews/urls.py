from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.review_queue, name="queue"),
    path("<int:document_id>/", views.review_document, name="review"),
]
