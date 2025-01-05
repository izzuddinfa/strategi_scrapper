import requests
import pandas as pd

class GetData:
    class BaseMode:
        def __init__(self, event, tahun, end_date=None):
            self.event = event
            self.tahun = tahun
            
            # Tentukan nilai default end_date berdasarkan tahun
            if end_date is None:
                self.end_date = pd.to_datetime(f'{tahun + 1}-01-05')
            else:
                self.end_date = pd.to_datetime(end_date)
            
            self.param = f"{event}::{13 if tahun == 2023 else event}"
            self.response = self._make_request()
            self._process_response()

        def _make_request(self):
            cookies = {
                '_ga_6CD720YJJK': 'GS1.1.1701955836.22.0.1701956371.0.0.0',
                '_ga_CF6YBE5JSB': 'GS1.1.1721549648.1.0.1721549648.60.0.1661575913',
            }
            headers = {
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json',
                'origin': 'https://strategi.kemenhub.go.id',
            }
            json_data = {
                'event': self.event,
                'provinsi': '',
                'moda': '',
                'endpoints': ['data-produksi'],
            }
            response = requests.post(
                'https://strategi.kemenhub.go.id/api/hubnet/data-pantau-produksi-seasonal',
                cookies=cookies,
                headers=headers,
                json=json_data,
            )
            # Cek status code respons
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                print(f"Response content: {response.text}")  # Cetak konten respons
                return None
            return response

        def _process_response(self):
            data = self.response.json().get('data', {})
            result = data.get('result', {}).get(self.param, {})
            clean_data = result.get('data_produksi', {}).get('data', {})

            # Inisialisasi atribut DataFrame
            self.jalan = pd.DataFrame(clean_data.get('jalan', None))
            self.asdp = pd.DataFrame(clean_data.get('asdp', None))
            self.laut = pd.DataFrame(clean_data.get('laut', None))
            self.udara = pd.DataFrame(clean_data.get('udara', None))
            self.stasiun = pd.DataFrame(clean_data.get('stasiun', None))
            self.toll = pd.DataFrame(clean_data.get('toll', None))
            self.arteri = pd.DataFrame(clean_data.get('arteri', None))

            # Bersihkan dan proses DataFrame
            dataframes = ['arteri', 'toll', 'jalan', 'asdp', 'laut', 'udara', 'stasiun']
            for name in dataframes:
                df = getattr(self, name, None)
                if df is not None:
                    df['tanggal'] = pd.to_datetime(df.get('tanggal'), errors='coerce')
                    for col in df.columns:
                        if col not in ['tanggal']:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                    if 'tanggal' in df.columns:
                        df = df[df['tanggal'] <= self.end_date]
                    setattr(self, name, df)

            # Atribut pergerakan
            self.pergerakan = pd.DataFrame({
                'tanggal': self.jalan['tanggal'] if 'tanggal' in self.jalan.columns else pd.NaT,
                'jalan': self.jalan.get('jml_pnp_brgkt', pd.Series(dtype=int)),
                'asdp': self.asdp.get('pnp', pd.Series(dtype=int)),
                'laut': self.laut.get('naik', pd.Series(dtype=int)),
                'udara': self.udara.get('jml_pnp_brkt', pd.Series(dtype=int)),
                'stasiun': self.stasiun.get('penumpang_berangkat_antarkota', pd.Series(dtype=int)),
            })

            # Atribut kumulatif
            self.kumulatif = pd.DataFrame({
                'moda': ['jalan', 'asdp', 'laut', 'udara', 'stasiun'],
                'kumulatif': [
                    self.pergerakan['jalan'].sum(),
                    self.pergerakan['asdp'].sum(),
                    self.pergerakan['laut'].sum(),
                    self.pergerakan['udara'].sum(),
                    self.pergerakan['stasiun'].sum(),
                ]
            })

    class Renops(BaseMode):
        def __init__(self, tahun=2024, end_date=None):
            super().__init__(event=19, tahun=tahun, end_date=end_date)

    class Komparasi(BaseMode):
        def __init__(self, tahun=2024, end_date=None):
            super().__init__(event=18, tahun=tahun, end_date=end_date)
