import logging

from django.conf import settings
from config import settings
from django.core.mail import send_mail
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from message.models import Attempt, Client, Mailing, Message
import datetime

logger = logging.getLogger(__name__)


def run_mailing():
    print('ok')
    now = datetime.datetime.now()
    mails = Mailing.objects.filter(status=True, next_date__isnull=False)
    after = now + datetime.timedelta(seconds=30)
    before = now - datetime.timedelta(seconds=30)
    mails = mails.filter(next_date__lt=after, next_date__gt=before)
    for mail in mails:
        message = Message.objects.get(user=mail.user)
        clients = Client.objects.filter(user=mail.user, is_active=True)
        response = True
        for client in clients:
            response = send_mail(
                subject=message.theme,
                message=message.message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email],
                fail_silently=False,
            )
            if response:
                pass
            else:
                break
        status = Attempt.objects.create(
            last_try=datetime.datetime.now, response=response, user=mail.user
        )
        status.save()
        mail.next_date = datetime.datetime.now() + mail.period
        mail.save()

    pass


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            run_mailing,
            trigger=CronTrigger(second="*/40"),  # Every 10 seconds
            id="run_mailing",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
