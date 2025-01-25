from django.shortcuts import render
from django.db.models import Q, Count  # Añadir Q aquí
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import ExtractHour
from .models import Product, InventoryMovement, PageVisit, WhatsAppQuery, Category  # Añadir Category aquí
import plotly.express as px
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Category, InventoryMovement
  
@login_required
def dashboard(request):
    # Estadísticas generales
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__lt=10).count()
    total_categories = Category.objects.count()


    # Manejo de búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        # Aplicar filtros de búsqueda
        products_list = Product.objects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        ).order_by('-views')
        
        low_stock_list = Product.objects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query),
            stock__lt=10
        )
    else:
        # Si no hay búsqueda, mostrar todos los productos
        products_list = Product.objects.all().order_by('-views')
        low_stock_list = Product.objects.filter(stock__lt=10)

    # Paginación de productos
    products_paginator = Paginator(products_list, 5)  # 5 productos por página
    products_page = request.GET.get('products_page', 1)

    try:
    # Intentamos obtener la página solicitada
        top_products = products_paginator.page(products_page)
    except PageNotAnInteger:
    # Si la página no es un número entero, mostramos la primera página
        top_products = products_paginator.page(1)
    except EmptyPage:
    # Si la página está fuera de rango, mostramos la última página
        top_products = products_paginator.page(products_paginator.num_pages)




    # Paginación de categorías
    # Asegúrate de que las categorías estén ordenadas antes de la paginación
    categories_list = Category.objects.all().order_by('name')  # Ordena por el campo 'name'
    categories_paginator = Paginator(categories_list, 5)  # 5 categorías por página
    categories_page = request.GET.get('categories_page', 1)

    try:
    # Intentamos obtener la página solicitada
        categories = categories_paginator.page(categories_page)
    except PageNotAnInteger:
    # Si la página no es un número entero, mostramos la primera página
        categories = categories_paginator.page(1)
    except EmptyPage:
    # Si la página está fuera de rango, mostramos la última página
        categories = categories_paginator.page(categories_paginator.num_pages)
        
        
        
        
        
        

    # Paginación de productos con stock bajo
    # Asegúrate de que los productos con stock bajo estén ordenados antes de la paginación
    low_stock_list = Product.objects.filter(stock__lt=10).order_by('name')  # Ordena por 'name' o el campo que prefieras
    low_stock_paginator = Paginator(low_stock_list, 5)  # 5 productos con stock bajo por página
    low_stock_page = request.GET.get('low_stock_page', 1)

    try:
        # Intentamos obtener la página solicitada
        low_stock_products = low_stock_paginator.page(low_stock_page)
    except PageNotAnInteger:
        # Si la página no es un número entero, mostramos la primera página
        low_stock_products = low_stock_paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostramos la última página
        low_stock_products = low_stock_paginator.page(low_stock_paginator.num_pages)
        
        
        
        
        
        

    # Estadísticas de visitas a páginas
    top_pages = PageVisit.objects.values('path') \
        .annotate(total_visits=Count('id')) \
        .values('path', 'total_visits', 'user_agent') \
        .order_by('-total_visits')

    # Análisis de consultas de WhatsApp (se mantiene igual)
    hours_data = {i: 0 for i in range(24)}
    whatsapp_counts = WhatsAppQuery.objects \
        .annotate(hour=ExtractHour('timestamp')) \
        .values('hour') \
        .annotate(count=Count('id'))

    for entry in whatsapp_counts:
        hours_data[entry['hour']] = entry['count']

    # Crear gráfico de distribución de consultas por hora
    fig = px.bar(
        x=list(hours_data.keys()),
        y=list(hours_data.values()),
        labels={'x': 'Hora del día (24h)', 'y': 'Número de consultas'}
    )
    fig.update_layout(
        title='Distribución de consultas por hora',
        xaxis=dict(
            ticktext=[f'{i:02d}:00' for i in range(24)],
            tickvals=list(range(24)),
            dtick=1,
            title='Hora del día'
        ),
        yaxis=dict(title='Número de consultas'),
        plot_bgcolor='rgba(0,0,0,0)',
        bargap=0.2
    )
    whatsapp_chart = fig.to_html(full_html=False)

    # Contexto para la plantilla
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_categories': total_categories,
        'top_products': top_products,
        'low_stock_products': low_stock_products,
        'top_pages': top_pages,
        'whatsapp_chart': whatsapp_chart,
        'categories': categories,
        'search_query': search_query,
       
    }

    return render(request, 'inventory/dashboard.html', context)


import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Product, Category, InventoryMovement


@login_required
def add_product(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price', 0)
            stock = request.POST.get('stock', 0)
            category_id = request.POST.get('category')
            
            if 'new_image' not in request.FILES:
                messages.error(request, 'Por favor selecciona una imagen.')
                return redirect('inventory:add_product')

            product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
            )
            
            if category_id:
                product.category_id = category_id

            if 'new_image' in request.FILES:
                product.image = request.FILES['new_image']
            
            product.save()
            messages.success(request, 'Producto agregado exitosamente.')
            return redirect('inventory:dashboard')

        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')
            return redirect('inventory:add_product')

    categories = Category.objects.all()
    return render(request, 'inventory/add_product.html', {'categories': categories})


@login_required
def update_stock(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        new_stock = int(request.POST['new_stock'])
        change = new_stock - product.stock
        
        InventoryMovement.objects.create(
            product=product,
            user=request.user,
            quantity_changed=change,
            notes=request.POST.get('notes', '')
        )
        
        product.stock = new_stock
        product.save()
        
        messages.success(request, 'Stock actualizado exitosamente')
        return redirect('dashboard')
    
    return redirect('dashboard')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from datetime import datetime
from .models import Product, InventoryMovement

@login_required
def generate_report(request):
    # Crear la respuesta HTTP con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'
    
    # Crear el objeto PDF usando reportlab
    p = canvas.Canvas(response, pagesize=letter)
    
    # Configurar el título
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, 750, "Reporte de Inventario")
    
    # Agregar fecha del reporte
    p.setFont("Helvetica", 12)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    p.drawString(50, 720, f"Fecha: {fecha}")
    
    # Encabezados de la tabla
    y = 680
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Productos en Stock")
    
    # Línea separadora
    y -= 20
    p.line(50, y, 550, y)
    
    # Contenido de la tabla
    y -= 20
    p.setFont("Helvetica", 12)
    for product in Product.objects.all():
        # Cambiar color según el nivel de stock
        if product.stock < 10:
            p.setFillColor(colors.red)
        else:
            p.setFillColor(colors.black)
            
        p.drawString(50, y, f"{product.name}")
        p.drawString(300, y, f"Stock: {product.stock}")
        p.drawString(400, y, f"Precio: S/ {product.price}")
        y -= 20
        
        if y < 50:  # Si llegamos al final de la página
            p.showPage()
            y = 750
    
    # Agregar sección de movimientos recientes
    p.showPage()
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 750, "Movimientos Recientes")
    
    y = 720
    p.setFont("Helvetica", 12)
    for movement in InventoryMovement.objects.all().order_by('-timestamp')[:10]:
        p.drawString(50, y, f"{movement.timestamp.strftime('%d/%m/%Y %H:%M')} - ")
        p.drawString(200, y, f"{movement.product.name} - ")
        p.drawString(350, y, f"Cambio: {movement.quantity_changed}")
        y -= 20
    
    # Guardar el PDF
    p.save()
    return response



# inventory/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, InventoryMovement
from .models import Product, Category
@login_required
def add_product(request):
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category')
            category = Category.objects.get(id=category_id) if category_id else None
            
            # Crear el producto con todos los campos, incluyendo la imagen, en una sola operación
            product = Product(
                name=request.POST['name'],
                description=request.POST['description'],
                price=request.POST['price'],
                stock=request.POST['stock'],
                category=category,
                views=0
            )
            
            # Asignar la imagen antes de guardar
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            # Guardar todo de una vez
            product.save()
            
            messages.success(request, 'Producto agregado exitosamente')
            return redirect('inventory:dashboard')
        except Exception as e:
            messages.error(request, f'Error al agregar el producto: {str(e)}')
            print(f"Error detallado: {e}")  # Para depuración
    
    categories = Category.objects.all()
    return render(request, 'inventory/add_product.html', {'categories': categories})










from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, InventoryMovement

@login_required
def update_stock(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            # Obtener y guardar el stock anterior
            old_stock = product.stock
            new_stock = int(request.POST.get('stock', 0))
            notes = request.POST.get('notes', '')
            
            # Calcular el cambio en el stock
            stock_change = new_stock - old_stock
            
            print(f"DEBUG - Stock change: Old={old_stock}, New={new_stock}, Change={stock_change}")
            
            # Actualizar todos los campos del producto
            product.name = request.POST.get('name', product.name)
            product.description = request.POST.get('description', product.description)
            product.price = float(request.POST.get('price', product.price))
            
            # Manejar la categoría
            category_id = request.POST.get('category')
            if category_id:
                product.category_id = category_id
            
            # Manejar la imagen
            if request.FILES.get('image'):
                product.image = request.FILES['image']
            
            # Crear nota detallada
            detailed_notes = (
                f"{notes}\n"
                f"Stock actualizado de {old_stock} a {new_stock}. "
                f"Cambio: {stock_change}"
            )
            
            # Registrar el movimiento de inventario ANTES de actualizar el producto
            movement = InventoryMovement.objects.create(
                product=product,
                user=request.user,
                quantity_changed=stock_change,
                notes=detailed_notes
            )
            
            print(f"DEBUG - Movement created: ID={movement.id}, Product={product.name}, Change={stock_change}")
            
            # Actualizar el stock y guardar el producto
            product.stock = new_stock
            product.save()
            
            messages.success(request, 
                f'Producto {product.name} actualizado exitosamente. '
                f'Stock anterior: {old_stock}, Nuevo stock: {new_stock}'
            )
            
            # Verificar que el movimiento se guardó
            try:
                verify_movement = InventoryMovement.objects.get(id=movement.id)
                print(f"DEBUG - Movement verified: {verify_movement}")
            except InventoryMovement.DoesNotExist:
                print("DEBUG - ERROR: Movement not found after creation")
                
        except ValueError as e:
            print(f"DEBUG - ValueError: {str(e)}")
            messages.error(request, f'Error en los valores ingresados: {str(e)}')
        except Exception as e:
            print(f"DEBUG - Exception: {str(e)}")
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
            
    return redirect('inventory:dashboard')


# inventory/views.py
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


###########################


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})




# inventory/views.py (añadir esta función)
from django.contrib import messages

@login_required
def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            name = product.name
            product.delete()
            messages.success(request, f'El producto "{name}" ha sido eliminado exitosamente.')
        except Product.DoesNotExist:
            messages.error(request, 'El producto no existe.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el producto: {str(e)}')
    
    return redirect('inventory:dashboard')


from django.views.decorators.http import require_http_methods
from inventory.forms import StaffUserCreationForm
from .models import InvitationCode

# inventory/views.py
@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = StaffUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Verificar el código de invitación
            invitation_code = form.cleaned_data['invitation_code']
            invitation = InvitationCode.objects.get(code=invitation_code)
            
            # Establecer permisos según el tipo de invitación
            if invitation.is_staff_invitation:
                user.is_staff = True
                user.is_superuser = True
            
            user.save()
            
            # Marcar el código como usado
            invitation.is_used = True
            invitation.used_by = user
            invitation.save()
            
            messages.success(request, 'Cuenta creada exitosamente')
            return redirect('login')
    else:
        form = StaffUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category

@login_required
def add_category(request):
    if request.method == 'POST':
        try:
            Category.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', '')
            )
            messages.success(request, 'Categoría agregada exitosamente')
            return redirect('inventory:dashboard')
        except Exception as e:
            messages.error(request, f'Error al agregar la categoría: {str(e)}')
            return redirect('inventory:dashboard')
    
    return render(request, 'inventory/add_category.html')

@login_required
def update_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        try:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.save()
            messages.success(request, f'Categoría {category.name} actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar la categoría: {str(e)}')
    return redirect('inventory:dashboard')

@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        try:
            category = Category.objects.get(id=category_id)
            name = category.name
            category.delete()
            messages.success(request, f'La categoría "{name}" ha sido eliminada exitosamente.')
        except Category.DoesNotExist:
            messages.error(request, 'La categoría no existe.')
        except Exception as e:
            messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    
    return redirect('inventory:dashboard')







# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TechnicalService, Product
from django.contrib import messages
from django.db.models import Q

@login_required
def service_list(request):
    # Obtener todos los servicios incluyendo los eliminados
    services = TechnicalService.objects.all()
    
    # Búsqueda por cliente o teléfono
    client_search = request.GET.get('client_search')
    phone_search = request.GET.get('phone_search')
    
    if client_search:
        services = services.filter(client_name__icontains=client_search)
    if phone_search:
        services = services.filter(client_phone__icontains=phone_search)
    
    services = services.order_by('-created_at')
    
    return render(request, 'inventory/service_list.html', {
        'services': services,
    })


@login_required
def add_service(request):
    if request.method == 'POST':
        service = TechnicalService.objects.create(
            service_name=request.POST['service_name'],
            client_name=request.POST['client_name'],
            client_phone=request.POST['client_phone'],
            description=request.POST['description'],
            status=request.POST['status']
        )
        if request.POST.getlist('parts'):
            service.parts.set(request.POST.getlist('parts'))
        
        messages.success(request, 'Servicio técnico creado exitosamente.')
        return redirect('inventory:service_list')

    return render(request, 'inventory/service_form.html', {
        'products': Product.objects.all()
    })



@login_required
def edit_service(request, ticket_id):
    service = get_object_or_404(TechnicalService, ticket_id=ticket_id)
    if request.method == 'POST':
        service.service_name = request.POST['service_name']
        service.client_name = request.POST['client_name']  # Nuevo campo
        service.description = request.POST['description']
        service.status = request.POST['status']
        service.save()
        
        parts = request.POST.getlist('parts')
        service.parts.set(parts)
        
        messages.success(request, 'Servicio técnico actualizado exitosamente.')
        return redirect('inventory:service_list')

    context = {
        'service': service,
        'products': Product.objects.all()
    }
    return render(request, 'inventory/service_form.html', context)

@login_required
def edit_service(request, ticket_id):
    service = get_object_or_404(TechnicalService, ticket_id=ticket_id)
    if request.method == 'POST':
        service.service_name = request.POST['service_name']
        service.client_name = request.POST['client_name']  # Nuevo campo
        service.description = request.POST['description']
        service.status = request.POST['status']
        service.save()
        
        parts = request.POST.getlist('parts')
        service.parts.set(parts)
        
        messages.success(request, 'Servicio técnico actualizado exitosamente.')
        return redirect('inventory:service_list')

    context = {
        'service': service,
        'products': Product.objects.all()
    }
    return render(request, 'inventory/service_form.html', context)

# views.py
@login_required
def delete_service(request, ticket_id):
    try:
        service = TechnicalService.objects.get(ticket_id=ticket_id)
        service.is_deleted = True  # En lugar de eliminar, marcamos como eliminado
        service.save()
        messages.success(request, 'Servicio técnico marcado como eliminado.')
    except TechnicalService.DoesNotExist:
        messages.error(request, 'El servicio técnico no existe.')
    return redirect('inventory:service_list')








import pandas as pd
from django.contrib import messages

@login_required
def import_products(request):
    if request.method == 'POST' and request.FILES['file']:
        try:
            file = request.FILES['file']
            # Determinar el tipo de archivo
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                messages.error(request, 'Formato de archivo no soportado. Use Excel (.xlsx) o CSV.')
                return redirect('inventory:dashboard')

            # Procesar cada fila
            for _, row in df.iterrows():
                try:
                    # Buscar o crear la categoría
                    category = None
                    if 'categoria' in row and pd.notna(row['categoria']):
                        category, _ = Category.objects.get_or_create(name=row['categoria'])

                    # Crear o actualizar producto
                    Product.objects.update_or_create(
                        name=row['nombre'],
                        defaults={
                            'description': row.get('descripcion', ''),
                            'price': row.get('precio', 0),
                            'stock': row.get('stock', 0),
                            'category': category
                        }
                    )
                except Exception as e:
                    messages.warning(request, f'Error en fila {_ + 2}: {str(e)}')
                    continue

            messages.success(request, 'Productos importados exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')
        
    return redirect('inventory:dashboard')



@login_required
def download_template(request):
    # Crear DataFrame de ejemplo
    df = pd.DataFrame({
        'nombre': ['Ejemplo Producto'],
        'descripcion': ['Descripción del producto'],
        'precio': [99.99],
        'stock': [10],
        'categoria': ['Ejemplo Categoría']
    })
    
    # Crear respuesta Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_importacion.xlsx'
    df.to_excel(response, index=False)
    
    return response






from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Product, InventoryMovement

@login_required
def inventory_detail(request):
    # Obtener todos los parámetros de búsqueda y filtros
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    stock_status = request.GET.get('stock_status')

    # Query base
    products = Product.objects.select_related('category').all()

    # Aplicar búsqueda si existe
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Aplicar filtros
    if category_id and category_id != 'all':
        products = products.filter(category_id=category_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if stock_status:
        if stock_status == 'low':
            products = products.filter(stock__lt=10)
        elif stock_status == 'out':
            products = products.filter(stock=0)

    # Ordenar productos
    products = products.order_by('name')

    # Paginación
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'products': products,
        'categories': Category.objects.all(),
        'current_filters': {
            'search': search_query,
            'category': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'stock_status': stock_status,
        }
    }

    return render(request, 'inventory/detail.html', context)


@login_required
def inventory_history(request):
    try:
        # Obtener todos los movimientos
        movements_list = InventoryMovement.objects.select_related('product', 'user').order_by('-timestamp')
        
        # Debug
        print(f"Total movimientos encontrados: {movements_list.count()}")
        for mov in movements_list:
            print(f"Movimiento: {mov.product.name} | {mov.quantity_changed} | {mov.user.username} | {mov.timestamp}")
        
        # Paginación
        paginator = Paginator(movements_list, 15)
        page = request.GET.get('page', 1)
        movements = paginator.get_page(page)
        
        context = {
            'movements': movements,
            'total_movements': movements_list.count()
        }
        
        return render(request, 'inventory/history.html', context)
    except Exception as e:
        print(f"Error en inventory_history: {str(e)}")
        messages.error(request, f'Error al cargar el historial: {str(e)}')
        return redirect('inventory:dashboard')

@login_required
def inventory_import_export(request):
    return render(request, 'inventory/import_export.html')




import pandas as pd
from django.http import HttpResponse
from datetime import datetime

@login_required
def import_products(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            # Determinar el tipo de archivo
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                messages.error(request, 'Formato de archivo no soportado. Use CSV o Excel.')
                return redirect('inventory:import_export')

            # Procesar los datos
            for _, row in df.iterrows():
                try:
                    # Buscar o crear la categoría
                    category, _ = Category.objects.get_or_create(name=row['categoria'])
                    
                    # Crear o actualizar el producto
                    product, created = Product.objects.update_or_create(
                        name=row['nombre'],
                        defaults={
                            'description': row['descripcion'],
                            'price': row['precio'],
                            'stock': row['stock'],
                            'category': category
                        }
                    )
                    
                    # Registrar el movimiento si es un producto nuevo
                    if created:
                        InventoryMovement.objects.create(
                            product=product,
                            user=request.user,
                            quantity_changed=product.stock,
                            notes="Producto importado"
                        )
                        
                except Exception as e:
                    messages.warning(request, f'Error al procesar fila {row["nombre"]}: {str(e)}')
                    continue

            messages.success(request, 'Productos importados correctamente')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')
            
    return redirect('inventory:dashboard')




from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

@login_required
def export_products(request):
    format_type = request.GET.get('format', 'csv')
    include_history = request.GET.get('include_history') is not None
    low_stock = request.GET.get('low_stock') is not None

    # Debug para verificar valores
    print(f"Include History: {include_history}, Low Stock: {low_stock}")

    # Filtrar productos
    products = Product.objects.select_related('category')
    if low_stock:
        products = products.filter(stock__lt=10)

    if format_type == 'pdf':
        buffer = BytesIO()
        # Usar landscape si hay muchas columnas
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo del título mejorado
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        
        elements.append(Paragraph("Reporte de Inventario", title_style))
        
        # Definir ancho de columnas
        col_widths = [100, 120, 60, 70]  # Ajustar según necesidad
        if include_history:
            col_widths.append(150)
            
        # Crear tabla con datos
        data = [['Producto', 'Categoría', 'Stock', 'Precio']]
        if include_history:
            data[0].append('Historial')
            
        for product in products:
            row = [
                product.name,
                product.category.name if product.category else 'Sin categoría',
                str(product.stock),
                f'S/ {product.price}'
            ]
            if include_history:
                movements = InventoryMovement.objects.filter(product=product).order_by('-timestamp')[:5]
                history = '\n'.join([
                    f"{m.timestamp.strftime('%d/%m/%Y %H:%M')} - {m.quantity_changed}"
                    for m in movements
                ])
                row.append(history)
            data.append(row)

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Estilo del encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.deepskyblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Estilo del contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Bordes y alineación
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de fila para mejor legibilidad
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
        
        # Agregar fecha de generación
        fecha_estilo = ParagraphStyle(
            'FechaEstilo',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=2  # Derecha
        )
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fecha_estilo))
        
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename=inventario_{timestamp}.pdf'
        
        return response
    
    else:
        # Para CSV y Excel
        products_data = []
        for product in products:
            data = {
                'Producto': product.name,
                'Categoría': product.category.name if product.category else 'Sin categoría',
                'Stock': product.stock,
                'Precio': f'S/ {product.price}'
            }
            
            if include_history:
                movements = InventoryMovement.objects.filter(product=product).order_by('-timestamp')
                history = '; '.join([
                    f"{m.timestamp.strftime('%d/%m/%Y %H:%M')} - Cambio: {m.quantity_changed}"
                    for m in movements
                ])
                data['Historial'] = history
            
            products_data.append(data)

        df = pd.DataFrame(products_data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename=inventario_{timestamp}.csv'
            df.to_csv(response, index=False, encoding='utf-8-sig')
        else:
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=inventario_{timestamp}.xlsx'
            df.to_excel(response, index=False)

        return response


from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from django.http import HttpResponse

def export_inventory_pdf(request):
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="historial_inventario.pdf"'

    # Crear el objeto PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Agregar encabezado
    header = Paragraph("<b>Historial de Inventario</b>", styles["Title"])
    subheader = Paragraph(
        f"Generado por: {request.user.username} <br/> Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"],
    )
    elements.append(header)
    elements.append(Spacer(1, 12))
    elements.append(subheader)
    elements.append(Spacer(1, 24))

    # Crear la tabla
    movements = InventoryMovement.objects.all()
    data = [["Fecha", "Producto", "Cambio", "Usuario"]]  # Encabezados de tabla
    for movement in movements:
        data.append([
            movement.timestamp.strftime("%d/%m/%Y %H:%M"),
            movement.product.name,
            f"{movement.quantity_changed:+}",
            movement.user.username,
        ])

    # Configurar estilos de la tabla
    table = Table(data, colWidths=[120, 220, 60, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))

    # Agregar la tabla al documento
    elements.append(table)

    # Construir el PDF
    doc.build(elements)

    return response


# inventory/views.py
@login_required
def inventory_import_export(request):
    return render(request, 'inventory/import_export.html')