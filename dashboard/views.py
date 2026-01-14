from django.views.generic import TemplateView
from user.mixins import AdminRequiredMixin


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404,render
from django.urls import reverse_lazy
from django.contrib import messages
from dashboard.models import Member
from .forms import MemberForm



# Create your views here.


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    login_url = '/admin/login/' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'dashboard'
        context['total_members'] = Member.objects.count()
        return context


  
    
#list user
class MemberListView(ListView):
    model = Member
    template_name = 'dashboard/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        # Sort members by name alphabetically
     return Member.objects.all().order_by('name')



#Create user

class MemberCreateView(CreateView):
    model = Member
    form_class = MemberForm
    template_name = 'dashboard/member_form.html'
    success_url = reverse_lazy('dashboard:member_list')

    def form_valid(self, form):
        messages.success(self.request, 'Member created successfully')
        return super().form_valid(form)



#update,edit
class MemberUpdateView(UpdateView):
    model = Member
    form_class = MemberForm
    template_name = 'dashboard/member_form.html'
    pk_url_kwarg = 'member_id'
    success_url = reverse_lazy('dashboard:member_list')

    def form_valid(self, form):
        messages.success(self.request, 'Member updated successfully')
        return super().form_valid(form)


#delete

class MemberDeleteView(DeleteView):
    model = Member
    template_name = 'dashboard/member_confirm_delete.html'
    pk_url_kwarg = 'member_id'
    success_url = reverse_lazy('dashboard:member_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Member deleted successfully')
        return super().delete(request, *args, **kwargs)
    

#activate and deactive

def member_toggle_active(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.is_active = not member.is_active
    member.save()
    return redirect('dashboard:member_list')

