from rest_framework import serializers
from .models import Rubro, Marca, Producto, Venta, DetalleVenta
from unidecode import unidecode

def estandarizar(texto):
    if not texto:
        return texto
    return unidecode(str(texto).strip().upper())


class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = '__all__'


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    rubro_nombre = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Producto
        fields = '__all__'

    def _resolve_marca(self, validated_data):
        nombre = validated_data.pop('marca_nombre', None)
        if nombre is not None:
            nombre = estandarizar(nombre)
            if nombre:
                marca, _ = Marca.objects.get_or_create(nombre=nombre)
                validated_data['marca'] = marca
            else:
                validated_data['marca'] = None
        return validated_data

    def _resolve_rubro(self, validated_data):
        nombre = validated_data.pop('rubro_nombre', None)
        if nombre is not None:
            nombre = estandarizar(nombre)
            if nombre:
                rubro, _ = Rubro.objects.get_or_create(nombre=nombre)
                validated_data['rubro'] = rubro
            else:
                rubro, _ = Rubro.objects.get_or_create(nombre='SIN RUBRO')
                validated_data['rubro'] = rubro
        return validated_data

    def create(self, validated_data):
        validated_data['nombre'] = estandarizar(validated_data.get('nombre', ''))
        if validated_data.get('descripcion'):
            validated_data['descripcion'] = estandarizar(validated_data['descripcion'])
        validated_data = self._resolve_marca(validated_data)
        validated_data = self._resolve_rubro(validated_data)

        codigo_barras = validated_data.get('codigo_barras', '')
        if codigo_barras:
            producto, creado = Producto.objects.update_or_create(
                codigo_barras=codigo_barras,
                defaults=validated_data
            )
            return producto

        nombre = validated_data.get('nombre', '')
        rubro = validated_data.get('rubro', None)
        if rubro:
            producto, creado = Producto.objects.update_or_create(
                nombre=nombre,
                rubro=rubro,
                defaults=validated_data
            )
            return producto

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['nombre'] = estandarizar(validated_data.get('nombre', ''))
        if validated_data.get('descripcion'):
            validated_data['descripcion'] = estandarizar(validated_data['descripcion'])
        validated_data = self._resolve_marca(validated_data)
        validated_data = self._resolve_rubro(validated_data)
        return super().update(instance, validated_data)


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['precio_unitario', 'subtotal']


class VentaSerializer(serializers.ModelSerializer):
    """Para el detalle de una venta (con items)."""
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'usuario', 'usuario_nombre', 'fecha', 'total', 'detalles']
        read_only_fields = ['usuario', 'fecha', 'total']


class VentaListSerializer(serializers.ModelSerializer):
    """Para el listado de ventas (sin items, más liviano)."""
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'usuario_nombre', 'fecha', 'total']
        read_only_fields = ['usuario', 'fecha', 'total']


class VentaCreateSerializer(serializers.Serializer):
    productos = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )

    def validate_productos(self, value):
        for item in value:
            if 'producto_id' not in item or 'cantidad' not in item:
                raise serializers.ValidationError(
                    'Cada producto debe tener "producto_id" y "cantidad".'
                )
            try:
                cantidad = int(item['cantidad'])
                if cantidad <= 0:
                    raise serializers.ValidationError('La cantidad debe ser mayor a 0.')
            except (ValueError, TypeError):
                raise serializers.ValidationError('La cantidad debe ser un número entero.')
        return value