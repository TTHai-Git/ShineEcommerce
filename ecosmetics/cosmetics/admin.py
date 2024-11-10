import cloudinary
from django.contrib import admin
from django import forms
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path

from cosmetics.models import *
from django.utils.html import mark_safe
from ckeditor_uploader.widgets import CKEditorUploadingWidget


# Register your models here.

class ScoreAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản lý điểm trực tuyến'


admin_site = ScoreAppAdminSite(name='myadmin')

# class ProductForm(forms.ModelForm):
#     description = forms.CharField(widget=CKEditorUploadingWidget)
#
#     class Meta:
#         model = Product
#         fields = '__all__'


# class MyProductAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'created_date', 'updated_date', 'active']
#     search_fields = ['name', 'description']
#     list_filter = ['id', 'created_date', 'name']
#     readonly_fields = ['my_image']
#     form = ProductForm
#
#     def my_image(self, instance):
#         if instance:
#             if instance.image is cloudinary.CloudinaryResource:
#                 return mark_safe(f"<img width='120' src='{instance.image.url}' />")
#
#             return mark_safe(f"<img width='120' src='/static/{instance.image.name}' />")


admin.site.register(Role)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Origin)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Payment)
admin.site.register(Shipment)
admin.site.register(PromotionTicket)

