# Kolay Kurulum Talimatları

Bu doküman, AI Görsel Oluşturma uygulamasının kurulumu ve çalıştırılması için basitleştirilmiş talimatlar içerir.

## 📋 Hızlı Başlangıç (Tek Adımda)

Tek bir komutla uygulamayı kurabilir ve başlatabilirsiniz:

```bash
chmod +x easy_setup.sh
./easy_setup.sh
```

Bu komut şunları yapacaktır:
1. Gerekli sistem bağımlılıklarını kontrol edip kurar
2. Python sanal ortamını oluşturur
3. Gerekli tüm Python kütüphanelerini yükler
4. Uygulamayı başlatır

## 📝 Manuel Kurulum

Adım adım kurulum yapmak isterseniz:

### 1. Sistem Bağımlılıklarını Yükleyin

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libgl1-mesa-glx ffmpeg
```

CentOS/RHEL:
```bash
sudo yum install -y python3-pip python3-devel mesa-libGL ffmpeg
```

### 2. Python Sanal Ortam Kurun

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Uygulamayı Başlatın

```bash
python3 main.py
```

## ❓ Sorun Giderme

**GPU Sorunları:**
- GPU kullanımı için NVIDIA ekran kartında CUDA kurulu olmalıdır
- Uygulama, GPU yoksa otomatik olarak CPU modunda çalışır

**Kütüphane Sorunları:**
- MoviePy yüklenmediyse: `pip install moviepy`
- OpenCV sorunları için: `pip install opencv-python --upgrade`
- OpenGL hatası için: `sudo apt-get install libgl1-mesa-glx`

**Diğer Sorunlar:**
Yardım için README.md dosyasına bakın.
