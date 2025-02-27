#!/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}AI Görsel Oluşturma - Model İndiricisi${NC}"
echo -e "${BLUE}=========================================${NC}"

# Çalışma dizinini belirle
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit

# Sanal ortamı aktifleştir
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}Sanal ortam bulunamadı! Önce kurulum yapın:${NC}"
    echo "./run.sh --install"
    exit 1
fi

# Kullanılabilir modelleri listele
echo -e "${BLUE}Kullanılabilir modeller:${NC}"
python -c "
from model_manager import list_available_models
models = list_available_models()
for model_id, model_info in models.items():
    print(f\"- {model_info['name']}\")
    print(f\"  ID: {model_id}\")
    print(f\"  Açıklama: {model_info.get('description', 'Açıklama yok')}\")
    print()
"

echo -e "${BLUE}Kullanılabilir LoRA'lar:${NC}"
python -c "
from model_manager import list_available_loras
loras = list_available_loras()
for lora_id, lora_info in loras.items():
    print(f\"- {lora_info['name']}\")
    print(f\"  ID: {lora_id}\")
    print(f\"  Açıklama: {lora_info.get('description', 'Açıklama yok')}\")
    print()
"

# İndirmek istediği modeli sor
echo -e "${YELLOW}Hangi modelleri indirmek istiyorsunuz? (boş bırakılırsa hepsi indirilir)${NC}"
echo -e "Seçenekler: ${GREEN}all${NC} (tümü), ${GREEN}loras${NC} (sadece LoRA'lar), veya belirli model ID'leri virgülle ayırarak"
read -r MODEL_INPUT

if [ -z "$MODEL_INPUT" ] || [ "$MODEL_INPUT" = "all" ]; then
    echo -e "${BLUE}Tüm modelleri indirme işlemi başlatılıyor...${NC}"
    python download_models.py
elif [ "$MODEL_INPUT" = "loras" ]; then
    echo -e "${BLUE}LoRA'ları indirme işlemi başlatılıyor...${NC}"
    python -c "
from model_manager import list_available_loras, download_lora
loras = list_available_loras()
for lora_id in loras:
    print(f'LoRA indiriliyor: {lora_id}')
    download_lora(lora_id)
    print(f'LoRA indirildi: {lora_id}')
"
else
    # Virgülle ayrılmış modelleri işle
    IFS=',' read -ra MODELS <<< "$MODEL_INPUT"
    echo -e "${BLUE}Seçili modelleri indirme işlemi başlatılıyor:${NC}"
    for model in "${MODELS[@]}"; do
        # Boşlukları temizle
        model=$(echo "$model" | tr -d '[:space:]')
        echo -e "- $model"
    done
    
    MODEL_ARGS=$(IFS=' '; echo "${MODELS[*]}")
    python download_models.py --model $MODEL_ARGS
fi

echo -e "${GREEN}İşlem tamamlandı!${NC}"
