# moto/signals.py

from decimal import Decimal
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from moto.models import Venta
from moto.models.cliente import Cliente
from moto.models.cuota_pago import CuotaPago
from moto.models.financiamiento import Financiamiento, _add_months
from moto.models.garantia import Garantia
from moto.models.mantenimiento import Mantenimiento
from moto.models.moto import Moto
from moto.models.resena import Resena


@receiver(post_save, sender=Cliente)
def enviar_bienvenida_cliente(sender, instance, created, **kwargs):
    """Se dispara automáticamente cada vez que se crea un Cliente nuevo (registro de app)."""
    if not created:
        return

    correo_destino = instance.correo or (instance.usuario.email if instance.usuario else None)

    if not correo_destino:
        return

    context = {
        'cliente': instance,
        'frontend_url': settings.FRONTEND_URL,
    }

    asunto = 'Bienvenido a Venta Motos 🏍️'
    html_content = render_to_string('emails/bienvenida.html', context)
    text_content = f'Hola {instance.nombre}, tu cuenta de cliente fue creada exitosamente.'

    email = EmailMultiAlternatives(
        subject=asunto,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[correo_destino],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send(fail_silently=True)


@receiver(post_save, sender=Venta)
def enviar_factura_correo(sender, instance, created, **kwargs):
    """Se dispara automáticamente cada vez que se crea una Venta nueva.

    El envío se difiere hasta que la transacción actual confirme (transaction.on_commit),
    porque los DetalleVenta de esta venta se crean DESPUÉS de Venta.objects.create()
    dentro de la misma transacción. Sin esto, el correo saldría con el detalle vacío.
    """
    if not created:
        return

    def _enviar():
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

    transaction.on_commit(_enviar)


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


@receiver(post_save, sender=Financiamiento)
def generar_cuotas_financiamiento(sender, instance, created, **kwargs):
    """
    Genera automáticamente el plan de cuotas (una por cada mes del plazo)
    apenas se crea un Financiamiento. Solo corre en la creación (created=True);
    si el financiamiento se edita después, las cuotas ya generadas no se tocan.
    """
    if not created:
        return

    cuota_mensual = instance.calcular_cuota_mensual()
    if not cuota_mensual:
        return

    total_cuotas = instance.plazo_meses
    monto_total = cuota_mensual * total_cuotas

    cuotas = []
    suma_generada = Decimal('0.00')
    for numero in range(1, total_cuotas + 1):
        if numero < total_cuotas:
            monto_cuota = cuota_mensual
            suma_generada += monto_cuota
        else:
            # La última cuota absorbe el residuo del redondeo para que la
            # suma total cuadre exacto con cuota_mensual * plazo_meses.
            monto_cuota = monto_total - suma_generada

        cuotas.append(CuotaPago(
            financiamiento=instance,
            numero_cuota=numero,
            fecha_vencimiento=_add_months(instance.fecha_inicio, numero),
            monto=monto_cuota,
            estado='pendiente',
        ))

    CuotaPago.objects.bulk_create(cuotas)