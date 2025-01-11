from django.urls import path
from app.views import (
    produk_list, produk_bisa_dijual, produk_create, produk_update, produk_delete, import_data_from_json
)

urlpatterns = [
    path('', produk_list, name='produk_list'),
    path('bisa-dijual/', produk_bisa_dijual, name='produk_bisa_dijual'),
    path('create/', produk_create, name='produk_create'),
    path('update/<int:pk>/', produk_update, name='produk_update'),
    path('delete/<int:pk>/', produk_delete, name='produk_delete'),
    path('import-data/', import_data_from_json, name='import_data'),
]
