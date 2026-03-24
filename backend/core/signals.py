from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Paciente, HistoriaClinica

@receiver(post_save, sender=Paciente)
def crear_historia_clinica(sender, instance, created, **kwargs):
    if created:
        HistoriaClinica.objects.create(paciente=instance)