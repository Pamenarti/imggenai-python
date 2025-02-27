#!/bin/bash

# Renk tanımları
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}      AI Görsel Oluşturma - Kolay Kurulum       ${NC}"
echo -e "${BLUE}=================================================${NC}"

# Çalışma dizinini algıla
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"

# İşletim sistemi bilgilerini al
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$ID
    echo -e "${YELLOW}İşletim sistemi: $OS_NAME ${PRETTY_NAME}${NC}"
else
    OS_NAME="unknown"
    echo -e "${YELLOW}İşletim sistemi belirlenemedi.${NC}"
fi

# GPU bilgilerini kontrol et
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}NVIDIA GPU bulundu. Model bilgisi:${NC}"
    nvidia-smi --query-gpu=name --format=csv,noheader
    HAS_GPU=true
else
    echo -e "${YELLOW}GPU bulunamadı. Sistem CPU modunda çalışacak.${NC}"
    HAS_GPU=false
fi

# Sistem bağımlılıklarını yükle
echo -e "\n${BLUE}Sistem bağımlılıkları yükleniyor...${NC}"
if [[ "$OS_NAME" == "ubuntu" || "$OS_NAME" == "debian" || "$OS_NAME" == "pop" || "$OS_NAME" == "mint" ]]; then
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv libgl1-mesa-glx ffmpeg
elif [[ "$OS_NAME" == "centos" || "$OS_NAME" == "rhel" || "$OS_NAME" == "fedora" ]]; then
    if [[ "$OS_NAME" == "fedora" ]]; then
        sudo dnf install -y python3-pip python3-devel mesa-libGL ffmpeg
    else
        sudo yum install -y python3-pip python3-devel mesa-libGL ffmpeg
    fi
else
    echo -e "${YELLOW}Sistem bağımlılıklarını otomatik yükleyemiyoruz. Lütfen manuel olarak yükleyin.${NC}"
    echo "Gerekli paketler: Python 3, pip, venv, OpenGL kütüphaneleri ve ffmpeg"
fi

# Python sanal ortam oluştur
echo -e "\n${BLUE}Python sanal ortamı oluşturuluyor...${NC}"
python3 -m venv venv
source venv/bin/activate

# Python bağımlılıklarını yükle
echo -e "\n${BLUE}Python bağımlılıkları yükleniyor...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Düşük bellek modu için sorgu
if [ "$HAS_GPU" = true ]; then
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
    if [ -n "$GPU_MEM" ] && [ "$GPU_MEM" -lt 6000 ]; then
        echo -e "${YELLOW}GPU belleği 6GB'dan az. Düşük bellek modu önerilir.${NC}"
        LOW_MEM="--low-memory"
    else
        LOW_MEM=""
    fi
else
    LOW_MEM="--low-memory"
fi

# Model indirme tercihi
echo -e "\n${YELLOW}Tüm modeller şimdi indirilsin mi? (y/N)${NC}"
read -r GET_MODELS
if [[ $GET_MODELS =~ ^[Yy] ]]; then
    echo -e "${BLUE}Modeller indiriliyor...${NC}"
    python -c "from model_manager import download_all_models; download_all_models()"
    echo -e "${GREEN}Modeller indirildi.${NC}"
else
    echo -e "${YELLOW}Modeller, ilk çalıştırmada indirilecek.${NC}"
fi

echo -e "\n${GREEN}Kurulum tamamlandı!${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Uygulamayı başlatmak için: ${GREEN}./run.sh${NC}"
echo -e "Düşük bellek modu için: ${GREEN}./run.sh --low-memory${NC}"
echo -e "İnternet üzerinden paylaşmak için: ${GREEN}./run.sh --share${NC}"
echo -e "${BLUE}============================================${NC}"

# Uygulamayı başlat
echo -e "\n${YELLOW}Uygulama şimdi başlatılsın mı? (Y/n)${NC}"
read -r START_APP
if [[ ! $START_APP =~ ^[Nn] ]]; then
    echo -e "${BLUE}Uygulama başlatılıyor...${NC}"
    ./run.sh $LOW_MEM
fi
