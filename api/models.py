from django.db import models


class Rubro(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rubro"

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "marca"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    codigo_barras = models.CharField(max_length=100, unique=True, blank=True, null=True)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, related_name="productos")
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "producto"

    def __str__(self):
        return f"{self.nombre} ({self.codigo_barras})"
    
    
class Venta(models.Model):
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,  # No se puede eliminar un usuario con ventas
        related_name='ventas'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'venta'
        ordering = ['-fecha']

    def __str__(self):
        return f'Venta #{self.id} - {self.usuario.username} - {self.fecha.strftime("%d/%m/%Y %H:%M")}'


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,  # No se puede eliminar un producto con ventas
        related_name='detalles_venta'
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_venta'

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre} (Venta #{self.venta.id})'