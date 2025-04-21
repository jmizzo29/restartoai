
from django.core.exceptions import PermissionDenied
from users.tokens import email_verification_token
from users import models, forms, mail
from django.contrib import messages
from django import shortcuts
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django.contrib.auth import mixins
from django.views import generic

# Create your views here.
User = auth.get_user_model()


class OrganizationAddUserView(LoginRequiredMixin, generic.FormView):
    template_name = 'organization/add_user.html'
    form_class = forms.OrganizationAddUserForm

    def dispatch(self, request, *args, **kwargs):
        # Only org admins can add users
        if not request.user.role == 'org_admin':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        organization = self.request.user.profile.organization

        # Check if user already exists
        if models.CustomUser.objects.filter(email=email).exists():
            messages.error(
                self.request, "A user with this email already exists.")
            return shortcuts.redirect('organization:add_user')

        # Create an invitation token
        token = email_verification_token.make_token(self.request.user)

        # Send invitation email
        mail.UserEmailManager().mail_organization_invitation(
            self.request,
            email,
            organization,
            token
        )

        messages.success(self.request, f"Invitation sent to {email}")
        return shortcuts.redirect('organization:dashboard')


class OrganizationInviteRegistrationView(generic.CreateView):
    template_name = 'organization/invite_registration.html'
    form_class = forms.UserRegistrationForm

    def get(self, request, *args, **kwargs):
        # Verify the token
        try:
            org_admin = models.CustomUser.objects.get(pk=kwargs['admin_id'])
            if not email_verification_token.check_token(org_admin, kwargs['token']):
                messages.error(request, "Invalid or expired invitation link.")
                return shortcuts.redirect('users:register')
        except models.CustomUser.DoesNotExist:
            messages.error(request, "Invalid invitation link.")
            return shortcuts.redirect('users:register')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = forms.IndividualProfileRegistrationForm()
        return context

    def form_valid(self, form):
        # Get the organization from the admin who sent the invite
        org_admin = models.CustomUser.objects.get(pk=self.kwargs['admin_id'])
        organization = org_admin.profile.organization

        # Create user
        user = form.save(commit=False)
        user.role = 'individual'
        user.is_premium = False
        user.save()

        # Create profile with the organization
        profile_form = forms.IndividualProfileRegistrationForm(
            self.request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.organization = organization
            profile.save()

        # Send verification email
        mail.UserEmailManager().mail_verification(self.request, user)

        messages.success(
            self.request, 'Account created! Please verify your email.')
        return shortcuts.redirect('users:login')


class ProfileListView(generic.ListView, mixins.LoginRequiredMixin):

    model = models.Profile
    paginate_by = 10
    ordering = ["-first_name", "-last_name"]

    def get_queryset(self):
        user_profile = self.request.user.profile
        organization = user_profile.organization
        qs = super().get_queryset()
        qs = qs.filter(organization=organization)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = self.request.user.profile.organization

        return context
