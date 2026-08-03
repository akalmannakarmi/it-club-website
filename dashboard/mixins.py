from django.contrib import messages
from django.db.models import Q


class DashboardContextMixin:
    active_page = None
    page_title = None
    success_message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.active_page:
            context["active_page"] = self.active_page
        if self.page_title:
            context["page_title"] = self.page_title
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class SearchableListMixin:
    search_fields = ()

    def get_queryset(self):
        qs = super().get_queryset().order_by("-updated_at")
        q = self.request.GET.get("search")
        if q and self.search_fields:
            clauses = Q()
            for field in self.search_fields:
                clauses |= Q(**{f"{field}__icontains": q})
            qs = qs.filter(clauses)
        return qs
