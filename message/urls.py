from django.conf import settings
from message.apps import MessageConfig
from django.urls import path
from django.conf.urls.static import static


from message.views import (
    AttemptListView,
    ClientCreateView,
    ClientDeleteView,
    ClientUpdateView,
    MailingBreak,
    MailingStart,
    MailingUpdateView,
    MessageCreateView,
    MessageListView,
    MessageUpdateView,
)

app_name = MessageConfig.name

urlpatterns = [
    path("", MessageListView.as_view(), name="index"),
    path("begin", MailingStart.as_view(), name="start"),
    path("stop", MailingBreak.as_view(), name="break"),
    path("create/", ClientCreateView.as_view(), name="client_create"),
    path("update/<int:pk>", ClientUpdateView.as_view(), name="client_update"),
    path("delete/<int:pk>", ClientDeleteView.as_view(), name="client_delete"),
    path("message_c/", MessageCreateView.as_view(), name="message_create"),
    path("message_u/<int:pk>", MessageUpdateView.as_view(), name="message_update"),
    path("mailing_u/<int:pk>", MailingUpdateView.as_view(), name="mailing_update"),
    path("attempts", AttemptListView.as_view(), name="attempts"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
