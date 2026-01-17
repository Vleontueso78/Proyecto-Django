from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .ConfigFinanciera import ConfigFinanciera


@receiver(post_save, sender=User)
def crear_config_usuario(sender, instance, created, **kwargs):
    """
    Crea automáticamente la ConfigFinanciera
    cuando se crea un nuevo usuario.
    """
    if created:
        ConfigFinanciera.objects.get_or_create(user=instance)