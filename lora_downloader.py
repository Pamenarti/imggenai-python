import os
import sys
import requests
import json
import logging
from pathlib import Path

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Yapılandırma
DEFAULT_LORA_DIR = Path("/home/agrotest2/imggenai/models/loras")
CONFIG_FILE = Path("/home/agrotest2/imggenai/models/model_info.json")

def setup_directories():
    """Gerekli dizinleri oluşturur"""
    if not DEFAULT_LORA_DIR.exists():
        logger.info(f"LoRA dizini oluşturuluyor: {DEFAULT_LORA_DIR}")
        DEFAULT_LORA_DIR.mkdir(parents=True, exist_ok=True)
    return True

def load_model_info():
    """Model bilgilerini yükler"""
    if not CONFIG_FILE.exists():
        logger.error(f"Model bilgi dosyası bulunamadı: {CONFIG_FILE}")
        return None
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Model bilgileri yüklenirken hata oluştu: {e}")
        return None

def list_available_loras():
    """Kullanılabilir LoRA modellerini listeler"""
    config = load_model_info()
    if not config or "loras" not in config:
        logger.error("Kullanılabilir LoRA bilgisi bulunamadı")
        return []
    
    return config["loras"]

def download_lora_manually(lora_id, output_path=None):
    """Manuel olarak bir LoRA modelini indir"""
    loras = list_available_loras()
    if not loras or lora_id not in loras:
        logger.error(f"LoRA bulunamadı: {lora_id}")
        return False
    
    lora_info = loras[lora_id]
    url = lora_info["url"]
    
    if not output_path:
        output_path = DEFAULT_LORA_DIR / f"{lora_id}.safetensors"
    
    logger.info(f"İndirme URL: {url}")
    logger.info(f"Çıktı yolu: {output_path}")
    
    try:
        logger.info("CivitAI, artık doğrudan API indirmeyi kısıtladığı için tarayıcınızla indirmeniz gerekmektedir.")
        logger.info("Lütfen aşağıdaki adımları izleyin:")
        logger.info(f"1. Tarayıcınızda şu URL'yi açın: {url}")
        logger.info(f"2. İndirilen dosyayı şu konuma kaydedin: {output_path}")
        logger.info(f"3. İndirme tamamlandıktan sonra uygulamayı yeniden başlatın.")
        
        # Kullanıcıdan giriş bekle
        input("İndirme işlemini tamamladığınızda Enter tuşuna basın...")
        
        # Dosyanın varlığını kontrol et
        if Path(output_path).exists():
            logger.info(f"LoRA başarıyla indirildi: {lora_id}")
            return True
        else:
            logger.error(f"LoRA dosyası bulunamadı: {output_path}")
            return False
    
    except Exception as e:
        logger.error(f"LoRA indirilirken hata oluştu: {e}")
        return False

def main():
    setup_directories()
    
    # Kullanılabilir LoRA'ları listele
    logger.info("Kullanılabilir LoRA modelleri:")
    loras = list_available_loras()
    
    if not loras:
        logger.error("Kullanılabilir LoRA bulunamadı")
        return
    
    for lora_id, lora_info in loras.items():
        print(f"- {lora_info['name']} ({lora_id}): {lora_info['description']}")
    
    # Kullanıcıdan LoRA seçimini al
    lora_id = input("\nİndirmek istediğiniz LoRA ID'sini girin: ")
    
    if lora_id not in loras:
        logger.error(f"Geçersiz LoRA ID: {lora_id}")
        return
    
    # LoRA'yı indir
    download_lora_manually(lora_id)

if __name__ == "__main__":
    main()
