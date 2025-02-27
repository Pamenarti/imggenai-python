#!/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Başlangıç banner'ı
show_banner() {
    echo -e "${BLUE}"
    echo "  _____                           _    ___ "
    echo " |_   _|                         | |  |__ \\"
    echo "   | |  _ __ ___   __ _  __ _  __| |     ) |"
    echo "   | | | '_ \` _ \\ / _\` |/ _\` |/ _\` |    / / "
    echo "  _| |_| | | | | | (_| | (_| | (_| |   / /_ "
    echo " |_____|_| |_| |_|\\__,_|\\__, |\\__,_|  |____|"
    echo "                          __/ |             "
    echo "                         |___/              "
    echo -e "${NC}"
    echo -e "${GREEN}AI Görsel Oluşturma Aracı${NC}"
    echo -e "-------------------------------------------\n"
}

show_banner

# Çalışma dizinini tespit et
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Komut satırı parametrelerini işle
INSTALL=false
DEBUG=false
PORT=7860
SHARE=false
LOW_MEMORY=false
DOWNLOAD_MODELS=false

while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --install|-i)
      INSTALL=true
      shift
      ;;
    --debug|-d)
      DEBUG=true
      shift
      ;;
    --port|-p)
      PORT="$2"
      shift 2
      ;;
    --share|-s)
      SHARE=true
      shift
      ;;
    --low-memory|-l)
      LOW_MEMORY=true
      shift
      ;;
    --download-models|-m)
      DOWNLOAD_MODELS=true
      shift
      ;;
    --help|-h)
      echo -e "${BLUE}AI Görsel Oluşturma - Yardım${NC}"
      echo ""
      echo "Kullanım: ./run.sh [seçenekler]"
      echo ""
      echo "Seçenekler:"
      echo "  -h, --help             Bu yardım mesajını gösterir"
      echo "  -i, --install          Bağımlılıkları yükler"
      echo "  -d, --debug            Hata ayıklama modunda çalıştırır"
      echo "  -p, --port PORT        Belirtilen portta çalıştırır (varsayılan: 7860)"
      echo "  -s, --share            İnternet üzerinden paylaşır (Gradio share)"
      echo "  -l, --low-memory       Düşük bellek modunda çalıştırır"
      echo "  -m, --download-models  Tüm modelleri indirir"
      echo ""
      exit 0
      ;;
    *)
      echo -e "${RED}Bilinmeyen seçenek: $key${NC}"
      exit 1
      ;;
  esac
done

# Sanal ortamın varlığını kontrol et, yoksa oluştur
if [ ! -d "venv" ] || [ "$INSTALL" = true ]; then
    echo -e "${BLUE}Python sanal ortamı kuruluyor...${NC}"
    python3 -m venv venv
fi

# Sanal ortamı aktifleştir
source venv/bin/activate

# Bağımlılıkları yükle
if [ "$INSTALL" = true ]; then
    echo -e "${BLUE}Bağımlılıklar yükleniyor...${NC}"
    pip install --upgrade pip setuptools wheel
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo -e "${YELLOW}requirements.txt dosyası bulunamadı. Temel bağımlılıklar yükleniyor...${NC}"
        pip install torch diffusers transformers accelerate gradio pillow opencv-python moviepy
    fi
    
    echo -e "${GREEN}Python bağımlılıkları yüklendi!${NC}"
fi

# Modelleri indir
if [ "$DOWNLOAD_MODELS" = true ]; then
    echo -e "${BLUE}Modeller indiriliyor...${NC}"
    python -c "from model_manager import download_all_models; download_all_models()"
    echo -e "${GREEN}Model indirme işlemi tamamlandı!${NC}"
fi

# Komut satırı parametrelerini oluştur
CMD_ARGS=""

if [ "$DEBUG" = true ]; then
    CMD_ARGS="$CMD_ARGS --debug"
fi

if [ "$SHARE" = true ]; then
    CMD_ARGS="$CMD_ARGS --share"
fi

if [ "$LOW_MEMORY" = true ]; then
    CMD_ARGS="$CMD_ARGS --low-memory"
fi

if [ -n "$PORT" ]; then
    CMD_ARGS="$CMD_ARGS --port $PORT"
fi

# Uygulamayı başlat
echo -e "${GREEN}Uygulama başlatılıyor...${NC}"
echo -e "Komut: python main.py $CMD_ARGS"
python main.py $CMD_ARGS

# Çıkış kodu kontrolü
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo -e "${RED}Uygulama hata ile sonlandı (kod: $exit_code)${NC}"
    echo -e "${YELLOW}Hata ayıklama için --debug seçeneğini kullanın.${NC}"
    exit $exit_code
fi
