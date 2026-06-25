# moto/mixins.py


class LogActividadMixin:
    """
    registra automáticamente las acciones de crear, actualizar y borrar en LogsActividad.
    """

    log_entidad = None  # Nombre de la entidad, ej: 'Moto', 'Venta', etc.

    def _get_entidad(self):
        return self.log_entidad or self.queryset.model.__name__

    def _crear_log(self, accion, datos_antes=None, datos_despues=None):
        from moto.models import LogsActividad
        LogsActividad.objects.create(
            usuario=self.request.user,
            accion=accion,
            entidad=self._get_entidad(),
            datos_antes=datos_antes,
            datos_despues=datos_despues,
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._crear_log(
            accion='CREATE',
            datos_despues=self._serializar(instance),
        )

    def perform_update(self, serializer):
        datos_antes = self._serializar(serializer.instance)
        instance = serializer.save()
        self._crear_log(
            accion='UPDATE',
            datos_antes=datos_antes,
            datos_despues=self._serializar(instance),
        )

    def perform_destroy(self, instance):
        datos_antes = self._serializar(instance)
        self._crear_log(
            accion='DELETE',
            datos_antes=datos_antes,
        )
        instance.delete()

    def _serializar(self, instance):
        try:
            serializer = self.get_serializer(instance)
            return serializer.data
        except Exception:
            return {'id': instance.pk}