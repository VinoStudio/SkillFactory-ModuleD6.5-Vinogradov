from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string
from decouple import config

from .models import Post


@receiver(m2m_changed, sender=Post.postCategory.through)
def subscribers_notify(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.postCategory.all()
        for category in categories:
            for subscriber in category.subscribers.all():
                html_content = render_to_string(
                    'send_mail_subscribe_to_news.html',
                    {
                        'user': subscriber,
                        'post': instance,
                    }
                )

                msg = EmailMultiAlternatives(
                    subject=f'{instance.title}',
                    body=f'{instance.text}',
                    from_email=config('DEFAULT_FROM_EMAIL'),
                    to=[f'{subscriber.email}'],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

#
#
#
