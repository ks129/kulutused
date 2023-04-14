from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, TemplateView, UpdateView

from kulutused.forms import DebtForm
from kulutused.models import Debt


class DebtCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    """Creation view for Debt model."""

    model = Debt
    success_url = '/'
    success_message = 'Võlgnevus on registreeritud.'
    template_name = 'kulutused/create_debt.html'
    form_class = DebtForm

    def form_valid(self, form: DebtForm) -> HttpResponseRedirect:
        """Inject currently authenticated user to model."""
        self.object = form.save(commit=False)
        self.object.payer = self.request.user
        self.object.save()
        super(DebtCreateView, self).form_valid(form)

        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self) -> dict:
        """Include request to form arguments."""
        kwargs = super(DebtCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class DebtUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Update view for Debt model."""

    model = Debt
    success_url = '/'
    success_message = 'Võlgnevus on uuendatud.'
    template_name = 'kulutused/edit_debt.html'
    form_class = DebtForm

    def get_queryset(self) -> Any:
        """Receive only logged-in user debt entries."""
        return super(DebtUpdateView, self).get_queryset().filter(payer=self.request.user)

    def get_form_kwargs(self) -> dict[str, dict]:
        """Include request to form arguments."""
        kwargs = super(DebtUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class HomeView(TemplateView):
    """Provide view for home page that includes graphs and general data."""

    template_name = 'kulutused/home.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Include necessary debt data for processing."""
        context = super(HomeView, self).get_context_data(**kwargs)

        context['total_per_user'] = {}
        context['pairs'] = {}
        debt_set = Debt.objects.all()
        for debt in debt_set.iterator():
            if debt.to_who not in context['total_per_user']:
                context['total_per_user'][debt.to_who] = 0

            if debt.payer not in context['total_per_user']:
                context['total_per_user'][debt.payer] = 0

            if (debt.payer, debt.to_who) not in context['pairs']:
                context['pairs'][(debt.payer, debt.to_who)] = 0

            if (debt.to_who, debt.payer) not in context['pairs']:
                context['pairs'][(debt.to_who, debt.payer)] = 0

            context['total_per_user'][debt.to_who] += debt.amount
            context['total_per_user'][debt.payer] -= debt.amount
            context['pairs'][(debt.to_who, debt.payer)] -= debt.amount
            context['pairs'][(debt.payer, debt.to_who)] += debt.amount

        if self.request.user.is_authenticated:
            context['my_debts'] = Debt.objects.filter(payer=self.request.user)
            context['others_debts'] = Debt.objects.filter(to_who=self.request.user)
        return context
