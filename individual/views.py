from django.shortcuts import render

# Create your views here.


def individual_dashboard_view(request):
    profile = request.user.profile
    context = {"profile": profile}
    return render(request, "individual/dashboard.html", context=context)
