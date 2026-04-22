from django.urls import path

from . import views

app_name = "cms_admin"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("linking/run/", views.run_auto_linker, name="run_auto_linker"),
]
