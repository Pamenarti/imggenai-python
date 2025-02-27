#!/bin/bash

# Renkli çıktı için
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}AI Görsel Oluşturma - İnternet Paylaşım Modu${NC}"

# Sanal ortamı aktifleştir
source venv/bin/activate

# Gradio paylaşım özelliğini düzelt
echo -e "${YELLOW}Gradio paylaşım özelliği düzeltiliyor...${NC}"
python3 fix_gradio_share.py

# Uygulamayı paylaşım özelliğiyle başlat
echo -e "${GREEN}Uygulama paylaşım özelliğiyle başlatılıyor...${NC}"
python3 main.py --share
