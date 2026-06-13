# moto/serializers/user.py

from rest_framework import serializers
from moto.models import Usuario, Cliente


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
        if Cliente.objects.filter(cedula=value).exists():
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

        nombre = validated_data.pop('nombre')
        apellido = validated_data.pop('apellido')
        cedula = validated_data.pop('cedula')
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