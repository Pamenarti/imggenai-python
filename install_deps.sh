#!/bin/bash

# Bu script, AI görsel oluşturma için gerekli tüm sistem bağımlılıklarını kurar

echo "==== AI Görsel Oluşturma - Sistem Bağımlılıkları Kurulum Scripti ===="

# Root yetkisi kontrol et
if [ "$EUID" -ne 0 ]; then
  echo "Bu script yönetici (sudo) hakları gerektirir."
  echo "Lütfen 'sudo ./install_deps.sh' komutunu kullanın."
  exit 1
fi

# Dağıtımı belirle
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$ID
    echo "Tespit edilen işletim sistemi: $OS_NAME"
else
    echo "İşletim sistemi belirlenemedi, Ubuntu varsayılacak."
    OS_NAME="ubuntu"
fi

# Ubuntu/Debian için paket yükleme
if [[ "$OS_NAME" == "ubuntu" || "$OS_NAME" == "debian" || "$OS_NAME" == "pop" || "$OS_NAME" == "mint" ]]; then
    echo "Ubuntu/Debian tabanlı sistem için kurulum yapılıyor..."
    apt-get update
    apt-get install -y \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        python3-dev \
        python3-pip \
        python3-venv \
        ffmpeg \
        python3-tk

    # Kullanıcı adını belirle
    USERNAME=$(logname || echo $SUDO_USER || echo $USER)
    
    # pip ile global paketleri yükle
    echo "Python temel paketleri yükleniyor..."
    pip3 install --upgrade pip
    pip3 install --upgrade setuptools wheel
    
# CentOS/RHEL/Fedora için paket yükleme
elif [[ "$OS_NAME" == "centos" || "$OS_NAME" == "rhel" || "$OS_NAME" == "fedora" ]]; then
    echo "CentOS/RHEL/Fedora için kurulum yapılıyor..."
    
    if [[ "$OS_NAME" == "fedora" ]]; then
        dnf install -y \
            mesa-libGL \
            glib2 \
            libSM \
            libXrender \
            libXext \
            python3-devel \
            python3-pip \
            ffmpeg
    else
        yum install -y epel-release
        yum install -y \
            mesa-libGL \
            glib2 \
            libSM \
            libXrender \
            libXext \
            python3-devel \
            python3-pip \
            ffmpeg
    fi

else
    echo "Desteklenmeyen işletim sistemi: $OS_NAME"
    echo "Lütfen gerekli kütüphaneleri manuel olarak yükleyin:"
    echo "- libGL (OpenGL)"
    echo "- Python3 ve pip"
    exit 1
fi

# Python sanal ortamı için temel paketleri yükle
if [ -d "/home/agrotest2/imggenai" ]; then
    cd /home/agrotest2/imggenai
    
    # Sanal ortamı oluştur
    python3 -m venv venv
    
    # Sanal ortamı etkinleştir
    source venv/bin/activate
    
    # Temel paketleri yükle
    pip install --upgrade pip
    pip install wheel setuptools
    pip install torch numpy moviepy opencv-python pillow
    pip install -r requirements.txt
    
    echo "Python sanal ortamı ve temel paketler yüklendi."
fi

echo "Sistem bağımlılıkları başarıyla yüklendi."
echo "Şimdi 'run.sh' scriptini çalıştırarak uygulamayı başlatabilirsiniz."
