#!/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}      AI Görsel Oluşturma - Temizleme Aracı      ${NC}"
echo -e "${BLUE}=================================================${NC}"

# Geçici dosyalar seçeneği
echo -e "\n${YELLOW}Geçici dosyaları temizle (önbellek, loglar vb.)? [E/h]${NC}"
read -r CLEAN_TEMP
if [[ ! $CLEAN_TEMP =~ ^[Hh] ]]; then
    echo -e "${BLUE}Önbellek dosyaları temizleniyor...${NC}"
    
    # Log dosyaları
    find . -name "*.log" -type f -delete
    
    # __pycache__ klasörleri
    find . -name "__pycache__" -type d -exec rm -rf {} +
    
    # Geçici dosyalar
    rm -rf ./.tmp/* ./tmp/* 2>/dev/null || true
    
    echo -e "${GREEN}Önbellek dosyaları temizlendi!${NC}"
fi

# Output klasörü için
if [ -d "./outputs" ]; then
    echo -e "\n${YELLOW}Çıktı klasörünü temizle? [e/H]${NC}"
    read -r CLEAN_OUTPUTS
    if [[ $CLEAN_OUTPUTS =~ ^[Ee] ]]; then
        echo -e "${BLUE}Çıktı klasörü temizleniyor...${NC}"
        rm -rf ./outputs/*
        echo -e "${GREEN}Çıktı klasörü temizlendi!${NC}"
    fi
fi

# Huggingface önbelleği
echo -e "\n${YELLOW}HuggingFace önbelleğini temizle (indirilen modeller silinecek)? [e/H]${NC}"
echo -e "${RED}DİKKAT: Modelleri tekrar indirmek gerekecek!${NC}"
read -r CLEAN_MODELS
if [[ $CLEAN_MODELS =~ ^[Ee] ]]; then
    echo -e "${BLUE}HuggingFace önbelleği temizleniyor...${NC}"
    HF_CACHE_DIR=$(python -c "import os; from huggingface_hub import constants; print(os.path.expanduser(constants.HUGGINGFACE_HUB_CACHE) if hasattr(constants, 'HUGGINGFACE_HUB_CACHE') else os.path.expanduser('~/.cache/huggingface'))" 2>/dev/null)
    
    if [ -z "$HF_CACHE_DIR" ]; then
        HF_CACHE_DIR=~/.cache/huggingface
    fi
    
    if [ -d "$HF_CACHE_DIR" ]; then
        echo -e "${RED}Modeller siliniyor: $HF_CACHE_DIR${NC}"
        rm -rf "$HF_CACHE_DIR"/*
        echo -e "${GREEN}HuggingFace önbelleği temizlendi!${NC}"
    else
        echo -e "${YELLOW}HuggingFace önbellek klasörü bulunamadı!${NC}"
    fi
fi

# Sanal ortam opsiyonu
echo -e "\n${YELLOW}Sanal ortamı temizle ve yeniden oluştur? [e/H]${NC}"
read -r CLEAN_VENV
if [[ $CLEAN_VENV =~ ^[Ee] ]]; then
    echo -e "${BLUE}Sanal ortam temizleniyor...${NC}"
    if [ -d "./venv" ]; then
        rm -rf ./venv
        echo "Sanal ortam silindi."
        
        echo -e "${BLUE}Yeni sanal ortam oluşturuluyor...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel
        
        if [ -f "requirements.txt" ]; then
            echo -e "${BLUE}Bağımlılıklar yükleniyor...${NC}"
            pip install -r requirements.txt
        fi
        
        echo -e "${GREEN}Sanal ortam yeniden oluşturuldu!${NC}"
    else
        echo -e "${YELLOW}Sanal ortam bulunamadı!${NC}"
    fi
fi

echo -e "\n${GREEN}Temizleme işlemi tamamlandı!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "  Uygulamayı çalıştırmak için: ${GREEN}./run.sh${NC}"
echo -e "${BLUE}=================================================${NC}\n"
