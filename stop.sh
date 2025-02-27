#!/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${RED}AI Görsel Oluşturma - Durdurma${NC}"
echo -e "${BLUE}============================================${NC}"

# PID dosyasını kontrol et
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    
    # PID hala çalışıyor mu kontrol et
    if ps -p "$PID" > /dev/null; then
        echo -e "${YELLOW}Uygulama durduruluyor (PID: $PID)...${NC}"
        kill "$PID"
        
        # Durma için 5 saniye bekle
        for i in {5..1}; do
            if ! ps -p "$PID" > /dev/null; then
                echo -e "${GREEN}Uygulama başarıyla durduruldu!${NC}"
                rm app.pid
                exit 0
            fi
            echo -e "${YELLOW}Bekleniyor ($i)...${NC}"
            sleep 1
        done
        
        # Hala çalışıyorsa, zorla durdur
        if ps -p "$PID" > /dev/null; then
            echo -e "${RED}Uygulama zorla durduruluyor...${NC}"
            kill -9 "$PID"
            echo -e "${GREEN}Uygulama zorla durduruldu!${NC}"
        fi
        
        rm app.pid
    else
        echo -e "${YELLOW}Uygulama zaten çalışmıyor gibi görünüyor.${NC}"
        rm app.pid
    fi
else
    echo -e "${YELLOW}PID dosyası bulunamadı, uygulama çalışmıyor olabilir.${NC}"
    
    # Yine de process kontrolü yap
    PIDS=$(pgrep -f "python main.py")
    
    if [ -n "$PIDS" ]; then
        echo -e "${YELLOW}Ancak şu PID'lerle çalışan uygulama bulundu: $PIDS${NC}"
        echo -e "${YELLOW}Durdurmak ister misiniz? (e/H)${NC}"
        read -r STOP
        
        if [[ $STOP =~ ^[Ee] ]]; then
            echo -e "${RED}Uygulamalar durduruluyor...${NC}"
            for pid in $PIDS; do
                kill "$pid" 2>/dev/null
            done
            echo -e "${GREEN}Tüm uygulamalar durduruldu!${NC}"
        fi
    else
        echo -e "${GREEN}Çalışan uygulama bulunamadı.${NC}"
    fi
fi
