from setuptools import setup, find_packages

setup(
    name="hamit_app",
    version="0.1.6",  # Sürümü artırıyoruz
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hamit-app=hamit_app.main:main',  # Terminal komutu = paket_adı.dosya_adı:fonksiyon_adı
        ],
    },
)
