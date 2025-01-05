from strategi import GetData as get
import pickle
from datetime import datetime
import pytz

wib = pytz.timezone('Asia/Jakarta')
now = datetime.now(wib)
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

years = [2023, 2024]
for year in years:
    renops = get.Renops(tahun=year)
    komparasi = get.Komparasi(tahun=year)

    # Membuat objek parent yang mencakup data dari GetRenops dan GetKomparasi
    data = get()
    data.renops = renops
    data.komparasi = komparasi

    # Menyimpan objek parent_data (yang mencakup GetRenops dan GetKomparasi) ke file dengan pickle
    with open(f'{timestamp}_data_{year}.pkl', 'wb') as file:
        pickle.dump(data, file)

    print(f"Data {year} telah disimpan.")