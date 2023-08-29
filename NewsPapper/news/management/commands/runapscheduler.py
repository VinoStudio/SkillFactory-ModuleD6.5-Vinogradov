import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from ...models import Category, Post, PostCategory, CategorySubscriber, User, Author
from django.urls import reverse
from django.utils import timezone
import datetime
from decouple import config
logger = logging.getLogger(__name__)


def send_weekly_news():

    categories = Category.objects.all()

    for category in categories:
        category_posts = Post.objects.filter(
            postCategory__name=category.name,
            postDate__gte=timezone.now() - datetime.timedelta(weeks=1),
        )
        for subscriber in category.subscribers.all():

            weekly_posts = list(category_posts)

            html_content = render_to_string(
                'weekly_news.html',
                {
                    'subscriber': subscriber,
                    'weekly_posts': weekly_posts,
                }
            )

            msg = EmailMultiAlternatives(
                subject='Weekly News',
                body='',
                from_email=config('DEFAULT_FROM_EMAIL'),
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):

        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_news,
            trigger=CronTrigger(week="*/1"),
            id="send_weekly_news",
            max_instances=1,
            replace_existing=True,
        )

        logger.info("Added job 'send_weekly_news'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")

            scheduler.start()

        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")

            scheduler.shutdown()

            logger.info("Scheduler shut down successfully!")