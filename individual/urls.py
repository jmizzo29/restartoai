from django.urls import path

from . import views

app_name = "individual"

urlpatterns = [
    path("", views.individual_dashboard_view, name="dashboard")
]
