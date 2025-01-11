from rest_framework import serializers
from .models import Produk, Kategori, Status

class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class ProdukSerializer(serializers.ModelSerializer):
    kategori = KategoriSerializer()
    status = StatusSerializer()

    class Meta:
        model = Produk
        fields = '__all__'
