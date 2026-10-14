from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .exceptions import AccountLocked
from .lockout import MAX_FAILED_ATTEMPTS, check_lockout, register_failure, reset_failures


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=['Administrador', 'Empleado'],
        write_only=True,
        required=False
    )
    nombre = serializers.CharField(source='first_name', required=False, allow_blank=True)
    apellido = serializers.CharField(source='last_name', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'nombre', 'apellido')

    def create(self, validated_data):
        role = validated_data.pop('role', 'Empleado')
        user = User.objects.create_user(**validated_data)
        if role == 'Administrador':
            user.is_staff = True
            user.save()
        group = Group.objects.get(name=role)
        user.groups.add(group)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if role:
            instance.groups.clear()
            group = Group.objects.get(name=role)
            instance.groups.add(group)

        instance.save()
        return instance
    
    
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')

    def get_role(self, obj):
        # Devuelve el primer grupo del usuario (o None si no tiene)
        group = obj.groups.first()
        return group.name if group else None
    
    
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    #forzamos que busque por email (tiene por defecto username)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reemplazamos el campo username por email
        self.fields['email'] = serializers.CharField(required=True)
        self.fields.pop('username', None)

    def validate(self, attrs):
        # Attrs ya tiene 'email' y 'password'
        email = attrs.get('email')
        password = attrs.get('password')

        # Si la cuenta está bloqueada ni intentamos validar credenciales
        locked_for = check_lockout(email)
        if locked_for:
            raise self._locked_error(locked_for)

        # Buscamos al usuario por email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            locked_for = register_failure(email)
            if locked_for:
                raise self._locked_error(locked_for)
            raise serializers.ValidationError('Credenciales inválidas.')

        # Verificamos la contraseña
        if not user.check_password(password):
            locked_for = register_failure(email)
            if locked_for:
                raise self._locked_error(locked_for)
            raise serializers.ValidationError('Credenciales inválidas.')

        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo.')

        # Login exitoso: limpiamos el contador de intentos fallidos
        reset_failures(email)

        # Generamos los tokens
        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return data

    @staticmethod
    def _locked_error(retry_after):
        minutes = max(1, round(retry_after / 60))
        return AccountLocked(
            {
                'message': (
                    'Cuenta bloqueada tras %d intentos fallidos. '
                    'Intentá de nuevo en %d minuto(s).' % (MAX_FAILED_ATTEMPTS, minutes)
                ),
                'retry_after': retry_after,
            },
            wait=retry_after,
        )
    
    
#Serializer para el auto-registro público. Fuerza siempre el rol 'Empleado' para evitar escalada de privilegios.
class RegisterPublicSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=8)
    nombre = serializers.CharField(source='first_name', required=True)
    apellido = serializers.CharField(source='last_name', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'nombre', 'apellido')

    def create(self, validated_data):
        # Siempre se crea como Empleado (sin opción a elegir)
        user = User.objects.create_user(**validated_data)
        group = Group.objects.get(name='Empleado')
        user.groups.add(group)
        return user