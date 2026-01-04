from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class AdminOnlyMixin(UserPassesTestMixin):
    """Only allow users in Admin group"""
    def test_func(self):
        # User must be authenticated AND in Admin group
        return self.request.user.groups.filter(name='Admin').exists()
    
    def handle_no_permission(self):
        # If not logged in, send to login page
        if not self.request.user.is_authenticated:
            return redirect('/admin/login/')
        # If logged in but not admin, redirect to home with message
        messages.error(self.request, 'You do not have permission to access the dashboard.')
        return redirect('/')


class DashboardView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    login_url = '/admin/login/'  # Where to redirect if not logged in
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'dashboard'
        return context