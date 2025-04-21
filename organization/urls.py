from django.urls import path

from . import views

app_name = "organization"

urlpatterns = [
    path("", views.ProfileListView.as_view(), name="dashboard"),
    path('add-user/', views.OrganizationAddUserView.as_view(), name='add_user'),
    path('invite/<int:admin_id>/<str:token>/',
         views.OrganizationInviteRegistrationView.as_view(),
         name='invite_register'),
]
