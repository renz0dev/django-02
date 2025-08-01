from rest_framework import serializers
from .models import Product, Category, ProductImage
import cloudinary.utils

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'name', 'image', 'uploaded_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        # Si la imagen existe, devuelve la URL completa de Cloudinary
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 
            'stock', 'views', 'created_at', 'image',
            'category', 'category_name', 'category_id'
        ]