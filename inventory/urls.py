# inventory/urls.py
# inventory/urls.py
from django.urls import path
from . import views
from . import api_views  # Importación correcta

app_name = 'inventory'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-category/', views.add_category, name='add_category'),
    path('update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/update/<int:category_id>/', views.update_category, name='update_category'),
    path('services/', views.service_list, name='service_list'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/edit/<int:ticket_id>/', views.edit_service, name='edit_service'),
    path('services/delete/<int:ticket_id>/', views.delete_service, name='delete_service'),
    path('import-products/', views.import_products, name='import_products'),
    path('download-template/', views.download_template, name='download_template'),
    path('product/<int:product_id>/update-stock/', views.update_stock, name='update_stock'),
    path('inventory/detail/', views.inventory_detail, name='inventory_detail'),
    path('inventory/history/', views.inventory_history, name='inventory_history'),
    path('inventory/import-export/', views.inventory_import_export, name='inventory_import_export'),
    path('export-products/', views.export_products, name='export_products'),  
    path('export-inventory-pdf/', views.export_inventory_pdf, name='export_inventory_pdf'),
    
    
    path('api/products/', api_views.ProductListCreateAPI.as_view(), name='api_product_list'),
    path('api/products/<int:pk>/', api_views.ProductRetrieveUpdateDestroyAPI.as_view(), name='api_product_detail'),
    path('api/categories/', api_views.CategoryListCreateAPI.as_view(), name='api_category_list'),
    path('api/categories/<int:pk>/', api_views.CategoryRetrieveUpdateDestroyAPI.as_view(), name='api_category_detail'),
    
    
    path('api/token/', api_views.CustomAuthToken.as_view(), name='api_token_auth'),
    
]




