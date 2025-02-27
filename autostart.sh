#!/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}AI Görsel Oluşturma - Otomatik Başlatma${NC}"
echo -e "${BLUE}============================================${NC}"

# Çalışma dizinini belirle
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit

# Sanal ortamı aktifleştir
if [ -d "venv" ]; then
    echo -e "${BLUE}Sanal ortam aktifleştiriliyor...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}Sanal ortam bulunamadı! Kurulum yapılıyor...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
fi

# Modelleri kontrol et
echo -e "${BLUE}Modeller kontrol ediliyor...${NC}"
python3 -c "
from model_manager import list_available_models, load_model
models = list_available_models()
print(f'{len(models)} model yapılandırılmış')
"

# Port boş mu kontrol et
PORT=7860
is_port_in_use() {
  nc -z localhost "$1" > /dev/null 2>&1
}

# Port kullanımdaysa alternatif port bul
while is_port_in_use $PORT; do
  echo -e "${YELLOW}Port $PORT kullanımda, alternatif port deneniyor...${NC}"
  PORT=$((PORT + 1))
done

# Uygulamayı başlat
echo -e "${GREEN}Uygulama port $PORT üzerinde başlatılıyor...${NC}"
nohup python main.py --port $PORT > app_log.txt 2>&1 &
APP_PID=$!

# PID'yi kaydet
echo $APP_PID > app.pid

echo -e "${GREEN}Uygulama arka planda başlatıldı (PID: $APP_PID)${NC}"
echo -e "Web arayüzü: ${BLUE}http://localhost:$PORT${NC}"
echo 
echo -e "${YELLOW}Log dosyası: $SCRIPT_DIR/app_log.txt${NC}"
echo -e "${YELLOW}Uygulamayı durdurmak için: ./stop.sh${NC}"
