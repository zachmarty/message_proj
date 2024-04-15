from django.db import models
from django.utils import timezone
from users.models import User
from datetime import timedelta, datetime

class Mailing(models.Model):
    first_start = models.DateField(blank=True, null=True, verbose_name="Первый запуск")
    status = models.BooleanField(
        blank=False, null=False, default=False, verbose_name="Актиность"
    )
    period = models.DurationField(default = timedelta(days=1), verbose_name = "Период")
    next_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        
    def __str__(self) -> str:
        return f"{self.id} {self.first_start}"

class Client(models.Model):
    full_name = models.CharField(max_length=50, verbose_name="ФИО")
    comment = models.TextField(
        max_length=200, verbose_name="Комментарий", blank=True, null=True
    )
    email = models.EmailField(unique=True, verbose_name="Почта")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False, verbose_name="Принадлежность к рассылке")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        
    def __str__(self) -> str:
        return f"{self.id} {self.full_name}"





class Message(models.Model):
    message = models.TextField(null=True, blank=True, verbose_name="Сообщение")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theme = models.CharField(
        max_length=100, blank=False, null=False, verbose_name="Тема"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        
    def __str__(self) -> str:
        return f"{self.id} {self.theme}"


class Attempt(models.Model):
    last_try = models.DateTimeField(
        verbose_name="Дата и время попытки"
    )
    response = models.BooleanField(verbose_name="Успешно")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"
        
    def __str__(self) -> str:
        return f"{self.id} {self.last_try}"
