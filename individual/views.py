from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from users import models

# Create your views here.


def individual_dashboard_view(request):
    profile = request.user.profile
    context = {"profile": profile}
    return render(request, "individual/dashboard.html", context=context)


class ProfileDetailView(generic.DetailView, LoginRequiredMixin):
    model = models.Profile
    template_name = "individual/profile_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
