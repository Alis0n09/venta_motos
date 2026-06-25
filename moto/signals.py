# moto/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from moto.models import Venta
from moto.models.financiamiento import Financiamiento
from moto.models.garantia import Garantia
from moto.models.mantenimiento import Mantenimiento
from moto.models.moto import Moto
from moto.models.resena import Resena


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


@receiver(pre_save, sender=Moto)
def registrar_historial_precio(sender, instance, **kwargs):
    """Se dispara antes de guardar una Moto. Si el precio cambió, guarda el historial."""
    if not instance.pk:
        return

    try:
        moto_anterior = Moto.objects.get(pk=instance.pk)
    except Moto.DoesNotExist:
        return

    if moto_anterior.precio != instance.precio:
        from moto.models import HistorialPrecio
        usuario = getattr(instance, '_usuario_modificacion', None)
        HistorialPrecio.objects.create(
            moto=moto_anterior,
            precio_anterior=moto_anterior.precio,
            precio_nuevo=instance.precio,
            usuario=usuario,
        )

@receiver(post_save, sender=Mantenimiento)
def registrar_historial_mantenimiento(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.cliente:
        return

    from moto.models import HistorialCliente
    moto_detalle = None
    if instance.moto and instance.moto.marca:
        moto_detalle = f"{instance.moto.marca.nombre} {instance.moto.modelo} ({instance.moto.anio})"

    HistorialCliente.objects.create(
        cliente=instance.cliente,
        tipo_evento='mantenimiento',
        detalle={
            'mantenimiento_id': instance.id,
            'moto': moto_detalle,
            'tipo': instance.tipo,
            'fecha': str(instance.fecha),
            'costo': str(instance.costo),
        }
    )


@receiver(post_save, sender=Garantia)
def registrar_historial_garantia(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.venta or not instance.venta.cliente:
        return

    from moto.models import HistorialCliente
    HistorialCliente.objects.create(
        cliente=instance.venta.cliente,
        tipo_evento='garantia',
        detalle={
            'garantia_id': instance.id,
            'venta_id': instance.venta.id,
            'fecha_inicio': str(instance.fecha_inicio),
            'fecha_fin': str(instance.fecha_fin),
            'tipo': instance.tipo,
        }
    )


@receiver(post_save, sender=Resena)
def registrar_historial_resena(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.cliente:
        return

    from moto.models import HistorialCliente
    moto_detalle = None
    if instance.moto and instance.moto.marca:
        moto_detalle = f"{instance.moto.marca.nombre} {instance.moto.modelo}"

    HistorialCliente.objects.create(
        cliente=instance.cliente,
        tipo_evento='resena',
        detalle={
            'resena_id': instance.id,
            'moto': moto_detalle,
            'rating': instance.rating,
            'comentario': instance.comentario,
        }
    )

@receiver(post_save, sender=Financiamiento)
def registrar_historial_financiamiento(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.venta or not instance.venta.cliente:
        return

    from moto.models import HistorialCliente
    HistorialCliente.objects.create(
        cliente=instance.venta.cliente,
        tipo_evento='financiamiento',
        detalle={
            'financiamiento_id': instance.id,
            'venta_id': instance.venta.id,
            'monto_financiado': str(instance.monto_financiado),
            'tasa_interes': str(instance.tasa_interes),
            'plazo_meses': instance.plazo_meses,
            'fecha_inicio': str(instance.fecha_inicio),
            'fecha_fin': str(instance.fecha_fin),
            'estado': instance.estado,
        }
    )
