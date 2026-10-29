from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InstitutionalProfile, User


@receiver(post_save, sender=User)
def create_institutional_profile(sender, instance, created, **kwargs):
    if created:
        InstitutionalProfile.objects.using(instance._state.db).get_or_create(user=instance)
