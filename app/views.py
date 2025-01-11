import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.http import HttpResponse
from app.models import Produk, Kategori, Status
from app.forms import ProdukForm
from django.http import JsonResponse
from datetime import datetime

# Menampilkan semua data
def produk_list(request):
    produk = Produk.objects.all().order_by('id_produk')
    return render(request, 'produk_list.html', {'produk': produk})

# Menampilkan data dengan status "bisa dijual"
def produk_bisa_dijual(request):
    produk = Produk.objects.filter(status__nama_status="bisa dijual")
    return render(request, 'produk_list.html', {'produk': produk})

# Tambah produk baru
def produk_create(request):
    if request.method == 'POST':
        form = ProdukForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('produk_list')
    else:
        form = ProdukForm()
    return render(request, 'produk_form.html', {'form': form})

# Edit produk
def produk_update(request, pk):
    produk = get_object_or_404(Produk, pk=pk)
    if request.method == 'POST':
        form = ProdukForm(request.POST, instance=produk)
        if form.is_valid():
            form.save()
            return redirect('produk_list')
    else:
        form = ProdukForm(instance=produk)
    return render(request, 'produk_form.html', {'form': form})

# Hapus produk
def produk_delete(request, pk):
    produk = get_object_or_404(Produk, pk=pk)
    if request.method == 'POST':
        produk.delete()
        return redirect('produk_list')
    return render(request, 'produk_confirm_delete.html', {'produk': produk})

def import_data_from_json(request):
    # Path file data.json
    file_path = './data.json'  # Ganti sesuai lokasi file Anda

    # Truncate database
    Produk.objects.all().delete()
    Kategori.objects.all().delete()
    Status.objects.all().delete()

    try:
        # Membaca file JSON
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)

        if json_data['error'] == 0:
            data_list = json_data['data']

            # Simpan kategori dan status terlebih dahulu untuk menghindari masalah ForeignKey
            kategori_mapping = {}
            status_mapping = {}

            # Simpan kategori
            for item in data_list:
                kategori_name = item['kategori']
                if kategori_name not in kategori_mapping:
                    kategori, created = Kategori.objects.get_or_create(nama_kategori=kategori_name)
                    kategori_mapping[kategori_name] = kategori

            # Simpan status
            for item in data_list:
                status_name = item['status']
                if status_name not in status_mapping:
                    status, created = Status.objects.get_or_create(nama_status=status_name)
                    status_mapping[status_name] = status

            # Simpan produk
            for item in data_list:
                Produk.objects.create(
                    id_produk=item['id_produk'],
                    nama_produk=item['nama_produk'],
                    harga=item['harga'],
                    kategori=kategori_mapping[item['kategori']],
                    status=status_mapping[item['status']],
                )

            # Reset auto-increment untuk Produk
            reset_auto_increment(Produk, 'id_produk')
            reset_auto_increment(Kategori, 'id_kategori')
            reset_auto_increment(Status, 'id_status')

            return JsonResponse({'message': 'Data berhasil diimport ke database dan auto-increment diperbarui!'})
        else:
            return JsonResponse({'error': 'File JSON tidak valid!'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def reset_auto_increment(model, field='id_produk'):
    """
    Perbarui sequence auto-increment agar tidak bertabrakan dengan data yang sudah ada.
    """
    table_name = model._meta.db_table  # Mendapatkan nama tabel dari model
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT MAX({field}) FROM {table_name};
        """)
        max_id = cursor.fetchone()[0]
        if max_id:
            # Perbarui sequence auto-increment ke nilai max_id + 1
            cursor.execute(f"""
                SELECT setval(pg_get_serial_sequence('{table_name}', '{field}'), {max_id + 1}, false);
            """)