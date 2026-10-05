from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer, EmailTokenObtainPairSerializer, RegisterPublicSerializer
from .permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

#CRUD Usuario
#Eliminamos RegisterView porque no queremos que los usuarios se registren por sí mismos, solo el administrador puede crear usuarios.
class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailTokenObtainPairSerializer

class RefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny,)
    
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
    
class RegisterPublicView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterPublicSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
            'nombre': user.first_name,
            'apellido': user.last_name,
            'role': 'Empleado',
        }, status=status.HTTP_201_CREATED)
    
    
#CRUD Administrador (para que cree, modifique y elimine empleados)
class AdminUserListView(generics.ListAPIView):
    """Lista todos los usuarios"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

class AdminUserCreateView(generics.CreateAPIView):
    """Crear un nuevo usuario"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (IsAdminUser,)

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Ver, modificar o eliminar un usuario específico"""
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        # Para actualizar usamos el RegisterSerializer (permite cambiar contraseña y rol)
        if self.request.method in ('PUT', 'PATCH'):
            return RegisterSerializer
        # Para ver detalles usamos el UserSerializer (sin contraseña)
        return UserSerializer

    def perform_destroy(self, instance):
        # Evita que un administrador se elimine a sí mismo
        if instance == self.request.user:
            raise serializers.ValidationError("No podés eliminar tu propio usuario.")
        instance.delete()