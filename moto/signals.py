# moto/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from moto.models import Venta


@receiver(post_save, sender=Venta)
def enviar_factura_correo(sender, instance, created, **kwargs):
    """Se dispara automáticamente cada vez que se crea una Venta nueva."""
    if not created:
        return

    cliente = instance.cliente
    correo_destino = cliente.correo or (cliente.usuario.email if cliente.usuario else None)

    if not correo_destino:
        return

    detalles = instance.detalles.select_related('moto', 'moto__marca').all()

    context = {
        'venta': instance,
        'cliente': cliente,
        'detalles': detalles,
        'total': instance.total,
        'metodo_pago': instance.get_metodo_pago_display(),
        'frontend_url': settings.FRONTEND_URL,
    }

    asunto = f'Factura de tu compra #{instance.id} — Venta Motos'
    html_content = render_to_string('emails/factura.html', context)
    text_content = f'Gracias por tu compra #{instance.id}. Total: ${instance.total}'

    email = EmailMultiAlternatives(
        subject=asunto,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[correo_destino],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send(fail_silently=True)