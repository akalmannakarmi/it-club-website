from django.views.generic import TemplateView, View
from user.mixins import AdminRequiredMixin


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404,render
from django.urls import reverse_lazy
from django.contrib import messages
from user.models import User
from .forms import MemberForm


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    login_url = '/admin/login/' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'dashboard'
        context['total_members'] = User.objects.count()
        return context


class MemberListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        # Sort members by name alphabetically
        return User.objects.all().order_by('username')


class MemberCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = MemberForm
    template_name = 'dashboard/member_form.html'
    success_url = reverse_lazy('dashboard:member_list')

    def form_valid(self, form):
        messages.success(self.request, 'Member created successfully')
        return super().form_valid(form)


class MemberUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = MemberForm
    template_name = 'dashboard/member_form.html'
    pk_url_kwarg = 'member_id'
    success_url = reverse_lazy('dashboard:member_list')

    def form_valid(self, form):
        messages.success(self.request, 'Member updated successfully')
        return super().form_valid(form)


class MemberDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'dashboard/member_confirm_delete.html'
    pk_url_kwarg = 'member_id'
    success_url = reverse_lazy('dashboard:member_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Member deleted successfully')
        return super().delete(request, *args, **kwargs)

class MemberDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'dashboard/member_confirm_delete.html'
    pk_url_kwarg = 'member_id'
    success_url = reverse_lazy('dashboard:member_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Member deleted successfully')
        return super().delete(request, *args, **kwargs)


class MemberActivateView(AdminRequiredMixin, View):
    def post(self, request, member_id):
        member = get_object_or_404(User, id=member_id)
        member.is_active = True
        member.save()

        return redirect("dashboard:member_list")


class MemberDeactivateView(AdminRequiredMixin, View):
    def post(self, request, member_id):
        member = get_object_or_404(User, id=member_id)
        member.is_active = False
        member.save()

        return redirect("dashboard:member_list")