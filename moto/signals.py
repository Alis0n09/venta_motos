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

        # Arma la URL absoluta de cada imagen: en un signal no hay "request"
        # disponible (no venimos de una vista HTTP), así que no se puede usar
        # request.build_absolute_uri(). El cliente de correo abre la imagen
        # desde su propia bandeja de entrada, en otra red, así que necesita
        # una URL pública completa (con dominio), no una ruta relativa tipo
        # "/media/motos/foto.jpg".
        for detalle in detalles:
            if detalle.moto and detalle.moto.imagen:
                detalle.moto.imagen_url_absoluta = f"{settings.BACKEND_URL}{detalle.moto.imagen.url}"
            else:
                detalle.moto.imagen_url_absoluta = None

        context = {
            'venta': instance,
            'cliente': cliente,
            'detalles': detalles,
            'total': instance.total,
            'metodo_pago': instance.get_metodo_pago_display(),
            'frontend_url': settings.FRONTEND_URL,
        }

        asunto = f'Factura de tu compra #{instance.id} — Victal Speed'
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


@receiver(post_save, sender=Venta)
def notificar_compra_cliente(sender, instance, created, **kwargs):
    """Crea una NotificacionesCliente ('Su compra fue realizada...') cada vez
    que se crea una Venta nueva. Se difiere con transaction.on_commit porque
    los DetalleVenta se crean después, en la misma transacción, y queremos
    describir las motos compradas en el mensaje.
    """
    if not created:
        return

    def _crear_notificacion():
        from moto.models import NotificacionesCliente

        detalles = instance.detalles.select_related('moto', 'moto__marca').all()
        if detalles:
            descripciones = []
            for detalle in detalles:
                moto = detalle.moto
                nombre_moto = f"{moto.marca.nombre} {moto.modelo}" if moto and moto.marca else (moto.modelo if moto else '')
                descripciones.append(f"{detalle.cantidad}x {nombre_moto}".strip())
            detalle_texto = ', '.join(descripciones)
            mensaje = f"Su compra #{instance.id} fue realizada con éxito: {detalle_texto}. Total: ${instance.total}."
        else:
            mensaje = f"Su compra #{instance.id} fue realizada con éxito. Total: ${instance.total}."

        NotificacionesCliente.objects.create(
            cliente=instance.cliente,
            tipo='compra',
            mensaje=mensaje[:255],
        )

    transaction.on_commit(_crear_notificacion)


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


@receiver(post_save, sender=Mantenimiento)
def notificar_mantenimiento_cliente(sender, instance, created, **kwargs):
    """Crea una NotificacionesCliente ('Su moto necesita mantenimiento...')
    cada vez que se registra un Mantenimiento nuevo para un cliente."""
    if not created:
        return

    if not instance.cliente:
        return

    from moto.models import NotificacionesCliente

    moto_detalle = None
    if instance.moto and instance.moto.marca:
        moto_detalle = f"{instance.moto.marca.nombre} {instance.moto.modelo}"
    elif instance.moto:
        moto_detalle = instance.moto.modelo

    if moto_detalle:
        mensaje = f"Su moto {moto_detalle} necesita mantenimiento: {instance.tipo}, programado para el {instance.fecha}."
    else:
        mensaje = f"Su moto necesita mantenimiento: {instance.tipo}, programado para el {instance.fecha}."

    NotificacionesCliente.objects.create(
        cliente=instance.cliente,
        tipo='mantenimiento',
        mensaje=mensaje[:255],
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


@receiver(post_save, sender=Garantia)
def notificar_garantia_cliente(sender, instance, created, **kwargs):
    """Crea una NotificacionesCliente cuando se activa una Garantía nueva."""
    if not created:
        return

    if not instance.venta or not instance.venta.cliente:
        return

    from moto.models import NotificacionesCliente
    mensaje = (
        f"Se activó su garantía ({instance.tipo}) para la compra #{instance.venta.id}, "
        f"válida del {instance.fecha_inicio} al {instance.fecha_fin}."
    )
    NotificacionesCliente.objects.create(
        cliente=instance.venta.cliente,
        tipo='garantia',
        mensaje=mensaje[:255],
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
def notificar_financiamiento_cliente(sender, instance, created, **kwargs):
    """Notifica al cliente sobre su financiamiento:
    - Al crearse en estado 'pendiente' (solicitud del cliente al pagar): avisa que quedó en revisión.
    - Al crearse ya 'activo' (lo registra un admin directamente): avisa que fue aprobado.
    - Al pasar de 'pendiente' a 'activo' (un admin aprueba la solicitud): avisa que fue aprobado.
    - Al pasar de 'pendiente' a 'cancelado' (un admin rechaza la solicitud): avisa que fue rechazado.
    """
    if not instance.venta or not instance.venta.cliente:
        return

    from moto.models import NotificacionesCliente
    estado_anterior = getattr(instance, '_estado_anterior', None)

    if created:
        if instance.estado == 'pendiente':
            mensaje = (
                f"Recibimos tu solicitud de financiamiento para la compra #{instance.venta.id}: "
                f"${instance.monto_financiado} a {instance.plazo_meses} meses. "
                f"Está en revisión, te avisaremos cuando sea aprobada."
            )
        else:
            mensaje = (
                f"Su financiamiento para la compra #{instance.venta.id} fue aprobado: "
                f"${instance.monto_financiado} a {instance.plazo_meses} meses "
                f"({instance.tasa_interes}% de interés anual)."
            )
    else:
        if estado_anterior == instance.estado:
            return
        if estado_anterior == 'pendiente' and instance.estado == 'activo':
            mensaje = (
                f"¡Tu financiamiento para la compra #{instance.venta.id} fue aprobado! "
                f"${instance.monto_financiado} a {instance.plazo_meses} meses "
                f"({instance.tasa_interes}% de interés anual)."
            )
        elif estado_anterior == 'pendiente' and instance.estado == 'cancelado':
            mensaje = (
                f"Tu solicitud de financiamiento para la compra #{instance.venta.id} "
                f"fue rechazada. Contáctanos si tienes dudas."
            )
        else:
            return

    NotificacionesCliente.objects.create(
        cliente=instance.venta.cliente,
        tipo='financiamiento',
        mensaje=mensaje[:255],
    )


@receiver(post_save, sender=Financiamiento)
def enviar_email_financiamiento(sender, instance, created, **kwargs):
    """Envía un correo al cliente cuando su financiamiento es aprobado o
    rechazado. Sigue el mismo patrón que enviar_factura_correo: se difiere
    con transaction.on_commit para que, en el caso de la aprobación, el plan
    de cuotas que arma generar_cuotas_financiamiento ya exista al momento
    de armar el correo (ese signal corre sincrónico, antes del commit, así
    que para cuando _enviar() se ejecuta las cuotas ya están creadas).
    """
    if not instance.venta or not instance.venta.cliente:
        return

    estado_anterior = getattr(instance, '_estado_anterior', None)

    if created:
        aprobado_recien = instance.estado == 'activo'
        rechazado_recien = False
    else:
        if estado_anterior == instance.estado:
            return
        aprobado_recien = estado_anterior == 'pendiente' and instance.estado == 'activo'
        rechazado_recien = estado_anterior == 'pendiente' and instance.estado == 'cancelado'

    if not aprobado_recien and not rechazado_recien:
        return

    def _enviar():
        cliente = instance.venta.cliente
        correo_destino = cliente.correo or (cliente.usuario.email if cliente.usuario else None)
        if not correo_destino:
            return

        if aprobado_recien:
            cuotas = instance.cuotas.order_by('numero_cuota').all()
            context = {
                'cliente': cliente,
                'financiamiento': instance,
                'venta': instance.venta,
                'cuotas': cuotas,
                'cuota_mensual': instance.calcular_cuota_mensual(),
                'frontend_url': settings.FRONTEND_URL,
            }
            asunto = 'Tu financiamiento fue aprobado — Victal Speed'
            template = 'emails/financiamiento_aprobado.html'
            text_content = (
                f'Tu financiamiento para la compra #{instance.venta.id} fue aprobado: '
                f'${instance.monto_financiado} a {instance.plazo_meses} meses, '
                f'{instance.tasa_interes}% de interés anual.'
            )
        else:
            context = {
                'cliente': cliente,
                'financiamiento': instance,
                'venta': instance.venta,
                'frontend_url': settings.FRONTEND_URL,
            }
            asunto = 'Tu solicitud de financiamiento fue rechazada — Victal Speed'
            template = 'emails/financiamiento_rechazado.html'
            text_content = (
                f'Tu solicitud de financiamiento para la compra #{instance.venta.id} fue rechazada. '
                f'Contáctate con tu vendedor o acude a la sucursal más cercana.'
            )

        html_content = render_to_string(template, context)
        email = EmailMultiAlternatives(
            subject=asunto,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[correo_destino],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)

    transaction.on_commit(_enviar)


@receiver(pre_save, sender=Financiamiento)
def _cachear_estado_anterior_financiamiento(sender, instance, **kwargs):
    """Guarda el estado anterior del financiamiento en la propia instancia,
    igual que se hace con CuotaPago, para saber si estado realmente cambió."""
    if not instance.pk:
        instance._estado_anterior = None
        return

    try:
        anterior = Financiamiento.objects.get(pk=instance.pk)
        instance._estado_anterior = anterior.estado
    except Financiamiento.DoesNotExist:
        instance._estado_anterior = None


@receiver(post_save, sender=Financiamiento)
def generar_cuotas_financiamiento(sender, instance, created, **kwargs):
    """
    Genera el plan de cuotas (una por cada mes del plazo) apenas el
    financiamiento queda en estado 'activo':
    - Si se crea directamente como 'activo' (lo registra un admin).
    - Si pasa de 'pendiente' a 'activo' (un admin aprueba la solicitud del cliente).
    Si el financiamiento se crea o queda en 'pendiente', NO se generan cuotas
    todavía — se generan recién cuando se aprueba. Nunca se regeneran cuotas
    si el financiamiento ya las tiene.
    """
    if instance.estado != 'activo':
        return

    estado_anterior = getattr(instance, '_estado_anterior', None)
    recien_activado = created or estado_anterior == 'pendiente'
    if not recien_activado:
        return

    if instance.cuotas.exists():
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


@receiver(pre_save, sender=CuotaPago)
def _cachear_estado_anterior_cuota(sender, instance, **kwargs):
    """Guarda el estado anterior de la cuota en la propia instancia, para que
    el post_save pueda saber si el estado realmente cambió (igual que se hace
    con el precio de Moto)."""
    if not instance.pk:
        instance._estado_anterior = None
        return

    try:
        anterior = CuotaPago.objects.get(pk=instance.pk)
        instance._estado_anterior = anterior.estado
    except CuotaPago.DoesNotExist:
        instance._estado_anterior = None


@receiver(post_save, sender=CuotaPago)
def notificar_cuota_pago_cliente(sender, instance, created, **kwargs):
    """Notifica al cliente cuando una cuota cambia de estado a 'pagada' o
    'vencida'. Las cuotas generadas en lote al crear el Financiamiento
    (bulk_create) no disparan señales, así que esto solo corre en
    actualizaciones posteriores (registrar un pago, un cron que marca
    vencidas, etc.), nunca en la creación inicial del plan de pagos.
    """
    if created:
        return

    estado_anterior = getattr(instance, '_estado_anterior', None)
    if estado_anterior == instance.estado:
        return

    financiamiento = instance.financiamiento
    if not financiamiento or not financiamiento.venta or not financiamiento.venta.cliente:
        return

    cliente = financiamiento.venta.cliente

    if instance.estado == 'pagada':
        mensaje = f"Registramos el pago de su cuota #{instance.numero_cuota} (${instance.monto})."
    elif instance.estado == 'vencida':
        mensaje = (
            f"Su cuota #{instance.numero_cuota} (${instance.monto}) está vencida. "
            f"Fecha límite: {instance.fecha_vencimiento}."
        )
    else:
        return

    from moto.models import NotificacionesCliente
    NotificacionesCliente.objects.create(
        cliente=cliente,
        tipo='pago',
        mensaje=mensaje[:255],
    )