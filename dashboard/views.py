from django.views.generic import TemplateView
from user.mixins import AdminRequiredMixin



class DashboardView( AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    login_url = '/admin/login/'  # Where to redirect if not logged in
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'dashboard'
        return context