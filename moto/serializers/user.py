# moto/serializers/user.py

from rest_framework import serializers
from moto.models import Usuario, Cliente, Staff
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


class RegisterSerializer(serializers.Serializer):
    username  = serializers.CharField(max_length=150)
    email     = serializers.EmailField()
    password  = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)
    nombre    = serializers.CharField(max_length=100, write_only=True)
    apellido  = serializers.CharField(max_length=100, write_only=True)
    cedula    = serializers.CharField(max_length=10, write_only=True)
    telefono  = serializers.CharField(max_length=15, write_only=True, required=False, allow_blank=True)

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate_cedula(self, value):
        if Usuario.objects.filter(cedula=value).exists():
            raise serializers.ValidationError('This cedula is already registered.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password2': 'Passwords do not match.'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        nombre   = validated_data.pop('nombre')
        apellido = validated_data.pop('apellido')
        cedula   = validated_data.pop('cedula')
        telefono = validated_data.pop('telefono', '')

        usuario = Usuario.objects.create_user(
            **validated_data,
            first_name=nombre,
            last_name=apellido,
            cedula=cedula,
            telefono=telefono,
        )

        Cliente.objects.create(
            usuario=usuario,
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            telefono=telefono,
            correo=usuario.email,
        )

        return usuario


class RegisterStaffSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email    = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    nombre   = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    cedula   = serializers.CharField(max_length=10)
    telefono = serializers.CharField(max_length=15, required=False, allow_blank=True)
    rol      = serializers.ChoiceField(choices=['admin', 'vendedor', 'bodeguero'])

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate_cedula(self, value):
        if len(value) != 10:
            raise serializers.ValidationError('La cédula debe tener 10 dígitos.')
        if Usuario.objects.filter(cedula=value).exists():
            raise serializers.ValidationError('Esta cédula ya está registrada.')
        return value

    def create(self, validated_data):
        rol      = validated_data.pop('rol')
        nombre   = validated_data.pop('nombre')
        apellido = validated_data.pop('apellido')
        cedula   = validated_data.pop('cedula')
        telefono = validated_data.pop('telefono', '')

        usuario = Usuario.objects.create_user(
            **validated_data,
            first_name=nombre,
            last_name=apellido,
            cedula=cedula,
            telefono=telefono,
            is_staff=True,
        )

        Staff.objects.create(usuario=usuario, rol=rol)
        return usuario


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id', 'username']

    def validate_email(self, value):
        request = self.context.get('request')
        if request and Usuario.objects.filter(email=value).exclude(pk=request.user.pk).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(min_length=8, write_only=True)
    new_password2    = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password2': 'Passwords do not match.'
            })
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            self.user = Usuario.objects.get(username=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("No existe un usuario con ese nombre de usuario.")
        if not self.user.email:
            raise serializers.ValidationError("Este usuario no tiene un correo registrado.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        if len(data['new_password']) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        try:
            uidb64, token = data['codigo'].split('.', 1)
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (ValueError, TypeError, OverflowError, Usuario.DoesNotExist):
            raise serializers.ValidationError("Código inválido.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("El código no es válido o ya expiró.")

        self.user = user
        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()