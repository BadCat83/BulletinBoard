from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Reply
from .tasks import send_email_through_celery


@receiver(post_save, sender=Reply)
def send_email(sender, instance, created, **kwargs) -> None:
    if created:
        send_email_through_celery(instance.pk)#.delay(instance.pk)
