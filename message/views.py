import datetime
from typing import Any
from config import settings
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import inlineformset_factory
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from message.forms import ClientForm, ClientListForm, MailingForm, MessageForm
from message.models import Attempt, Client, Mailing, Message
from users.models import User


# Create your views here.
class MessageListView(ListView):
    model = Mailing

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user"] = self.request.user
            try:
                context["message"] = Message.objects.get(user=self.request.user)
            except:
                pass
            context["clients"] = Client.objects.filter(user=self.request.user)
        return context

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset

class AttemptListView(ListView, LoginRequiredMixin):
    model = Attempt
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = Attempt.objects.filter(user = self.request.user).order_by('last_try')
        return queryset.reverse()

class MailingStart(TemplateView, LoginRequiredMixin):
    http_method_names = ['get']
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        clients = Client.objects.filter(user = self.request.user, is_active = True)
        message = Message.objects.get(user = self.request.user)
        mailing = Mailing.objects.get(user = self.request.user)
        mailing.next_date = datetime.datetime.now() + mailing.period
        mailing.status = True
        mailing.save()
        response = True
        for client in clients:
            response = send_mail(
                subject=message.theme,
                message= message.message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email],
                fail_silently=False
            )
            if response:
                pass
            else:
                break
        status = Attempt.objects.create(last_try = datetime.datetime.now(), response = response, user = self.request.user)
        status.save()
        return HttpResponseRedirect(self.request.META['HTTP_REFERER'])

class MailingBreak(TemplateView, LoginRequiredMixin):
    http_method_names = ['get']
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        mailing = Mailing.objects.get(user = self.request.user)
        mailing.status = False
        mailing.save()
        return HttpResponseRedirect(self.request.META['HTTP_REFERER'])

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("message:index")

    def form_valid(self, form):
        new_client = form.save(commit=False)
        new_client.user = self.request.user
        mailing = Mailing.objects.get(user=self.request.user)
        new_client.mailing = mailing
        new_client.save()
        
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("message:index")

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        self.object = Client.objects.get(id=self.kwargs["pk"])
        if self.object.user != self.request.user:
            raise Http404
        return self.object


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy("message:index")

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        self.object = Client.objects.get(id=self.kwargs["pk"])
        if self.object.user != self.request.user:
            raise Http404
        return self.object


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("message:index")

    def form_valid(self, form):
        new_client = form.save(commit=False)
        new_client.user = self.request.user
        new_client.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("message:index")

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        self.object = Message.objects.get(id=self.kwargs["pk"])
        if self.object.user != self.request.user:
            raise Http404
        return self.object


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("message:index")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        MailingFormset = inlineformset_factory(
            User, Client, form=ClientListForm, extra=0
        )
        if self.request.method == "POST":
            context["formset"] = MailingFormset(
                self.request.POST, instance=self.request.user
            )
        else:
            context["formset"] = MailingFormset(instance=self.request.user)
        return context

    def form_valid(self, form):
        formset = self.get_context_data()["formset"]
        if formset.is_valid():
            formset.instance = self.request.user
            formset.save()
        return super().form_valid(form)

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        self.object = Mailing.objects.get(id=self.kwargs["pk"])
        if self.object.user != self.request.user:
            raise Http404
        return self.object
