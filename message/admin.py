from django.contrib import admin
from message.models import Client, Message, Mailing, Attempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "is_active")
    list_filter = ("full_name",)
    search_fields = ("full_name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "theme")
    list_filter = ("theme", "user")
    search_fields = ("theme", "message")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "first_start", "status")
    list_filter = ("status", "user")
    search_fields = ("first_start", "status")


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "last_try", "response")
    list_filter = ("response", "user")
    search_fields = ("last_try",)


# Register your models here.
