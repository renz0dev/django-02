from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ProductImage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='products/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField()
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class InventoryMovement(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)  # Notas generales
    changed_fields = models.JSONField(default=dict, blank=True)  # Campos modificados

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.product.name} - {self.quantity_changed} - {self.timestamp}"

    def get_changed_fields_display(self):
        """
        Método para devolver una representación legible de los campos cambiados.
        """
        field_names = {
            "name": "Nombre",
            "image": "Imagen",
            "price": "Precio",
            "category": "Categoría"
        }
        changes = [field_names.get(field, field) for field, changed in self.changed_fields.items() if changed]
        return ", ".join(changes) if changes else "Sin cambios"

class PageVisit(models.Model):
    path = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.path} - {self.timestamp}"

class WhatsAppQuery(models.Model):
    QUERY_TYPES = (
        ('PRODUCT', 'Consulta de Producto'),
        ('PRICE', 'Consulta de Precio'),
        ('STOCK', 'Consulta de Stock'),
        ('OTHER', 'Otra Consulta')
    )
    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    query_type = models.CharField(max_length=10, choices=QUERY_TYPES)
    phone_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.query_type} - {self.timestamp}"

class InvitationCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_staff_invitation = models.BooleanField(default=False)

    def __str__(self):
        return f"Código: {self.code} ({'Usado' if self.is_used else 'No usado'})"

class TechnicalService(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registrado'),
        ('in_progress', 'En Curso'),
        ('completed', 'Terminado'),
    ]

    ticket_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=200, verbose_name="Nombre del Servicio")
    client_name = models.CharField(max_length=200, verbose_name="Nombre del Cliente", default="Cliente Desconocido")
    client_phone = models.CharField(max_length=20, verbose_name="Teléfono del Cliente", default="Telefono Desconocido")
    description = models.TextField(verbose_name="Descripción/Detalles")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='registered'
    )
    parts = models.ManyToManyField(Product, blank=True, related_name='services')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Servicio: {self.service_name} - Estado: {self.status}"