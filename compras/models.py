from django.db import models


class Compra(models.Model):
    descripcion = models.CharField(max_length=200)
    codigo_cotizacion = models.CharField(max_length=100)
    precio = models.IntegerField()
    cantidad = models.IntegerField()
    empresa = models.CharField(max_length=100)
    destino = models.CharField(max_length=200)
    tiempo_entrega = models.CharField(max_length=200)
    observaciones = models.CharField(max_length=100)
    foto_producto = models.ImageField(
        upload_to="fotos_empleados/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def es_extension_valida(self):
        extensiones_validas = [".jpg", ".jpeg", ".png", ".gif"]
        return any(
            self.foto_empleado.name.lower().endswith(ext) for ext in extensiones_validas
        )

    """ la clase Meta dentro de un modelo se utiliza para proporcionar metadatos adicionales sobre el modelo."""

    class Meta:
        db_table = "compras"
        ordering = ["-created_at"]
        unique_together = (("codigo_cotizacion", "empresa"),)
