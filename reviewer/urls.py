from django.urls import path
from .views import (
    home_view,
    download_csv,
)

app_name = "reviewer"

urlpatterns = [
    path("", home_view, name="home"),
    path("download-csv/", download_csv, name="download_csv"),
]
