#!/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Gradio güncellemesi yapılıyor...${NC}"

# Sanal ortamı aktifleştir
source venv/bin/activate

# Mevcut Gradio versiyonunu kontrol et
echo -e "${YELLOW}Mevcut Gradio versiyonu:${NC}"
pip show gradio | grep Version

# Gradio'yu güncelle
echo -e "${GREEN}Gradio güncelleniyor...${NC}"
pip install --upgrade gradio

# Yeni versiyonu kontrol et
echo -e "${GREEN}Güncellenen Gradio versiyonu:${NC}"
pip show gradio | grep Version

echo -e "${BLUE}İşlem tamamlandı.${NC}"
echo -e "${YELLOW}Not: Güncelleme sonrası queue API değişmiş olabilir, main.py dosyasındaki değişiklikleri kontrol edin.${NC}"
