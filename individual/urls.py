from django.urls import path

from . import views

app_name = "individual"

urlpatterns = [
    path("", views.individual_dashboard_view, name="dashboard"),
    path("profile/<int:pk>", views.ProfileDetailView.as_view(), name="profile-detail")
]
