# inventory/admin.py
from django.utils.html import format_html
from django.contrib import admin
from .models import Product, InventoryMovement, PageVisit, WhatsAppQuery, Category, TechnicalService

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock', 'price', 'views', 'image_preview')  # Agrega image_preview
    search_fields = ('name', 'description')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;"/>', obj.image.url)
        return "No Image"

    image_preview.short_description = "Imagen"  # Cambia el nombre de la columna en el admin

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'quantity_changed', 'timestamp')
    list_filter = ('user', 'timestamp')

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('path', 'user_agent', 'timestamp', 'duration')
    list_filter = ('timestamp',)

@admin.register(WhatsAppQuery)
class WhatsAppQueryAdmin(admin.ModelAdmin):
    list_display = ('product', 'query_type', 'timestamp', 'resolved')
    list_filter = ('query_type', 'resolved', 'timestamp')
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(TechnicalService)
class TechnicalServiceAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'service_name', 'client_name', 'client_phone', 'status', 'created_at', 'is_deleted')
    list_filter = ('status', 'is_deleted', 'created_at')
    search_fields = ('ticket_id', 'service_name', 'client_name', 'client_phone')
    readonly_fields = ('ticket_id', 'created_at')
    filter_horizontal = ('parts',)  # Para la relación many-to-many con productos
    
    fieldsets = (
        ('Información del Servicio', {
            'fields': ('ticket_id', 'service_name', 'description', 'status')
        }),
        ('Información del Cliente', {
            'fields': ('client_name', 'client_phone')
        }),
        ('Repuestos', {
            'fields': ('parts',)
        }),
        ('Información Adicional', {
            'fields': ('created_at', 'is_deleted')
        })
    )
 
    
    