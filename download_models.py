#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import torch
from pathlib import Path
from huggingface_hub import login
from tqdm import tqdm
from model_manager import list_available_models, list_available_loras, download_lora

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("model_download.log")
    ]
)
logger = logging.getLogger(__name__)

def check_gpu_info():
    """GPU bilgilerini kontrol et"""
    if not torch.cuda.is_available():
        logger.warning("CUDA destekli GPU bulunamadı. Model indirme işlemi CPU üzerinde yapılacak.")
        return False, "", 0
    
    device_name = torch.cuda.get_device_name(0)
    device_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
    
    logger.info(f"GPU: {device_name} ({device_memory:.2f} GB)")
    return True, device_name, device_memory

def verify_disk_space(models_dir):
    """Disk alanını kontrol et"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(models_dir)
        
        # GB cinsinden dönüştür
        free_gb = free / (1024**3)
        logger.info(f"Kullanılabilir disk alanı: {free_gb:.2f} GB")
        
        if free_gb < 10:
            logger.warning(f"Uyarı: Kullanılabilir disk alanı çok az ({free_gb:.2f} GB). Model indirmek için en az 10 GB önerilir.")
        
        return free_gb
    except Exception as e:
        logger.error(f"Disk alanı kontrol edilemedi: {e}")
        return None

def download_models(models_to_download=None, models_dir=None, use_auth=False, hf_token=None):
    """Belirtilen modelleri indir"""
    try:
        # HuggingFace kimlik doğrulaması
        if use_auth:
            if hf_token:
                login(token=hf_token)
                logger.info("HuggingFace kimlik doğrulaması yapıldı.")
            else:
                logger.warning("HuggingFace token belirtilmedi. Bazı modeller indirilemeyebilir.")
                try:
                    login()
                    logger.info("Mevcut HuggingFace kimliği kullanıldı.")
                except:
                    logger.warning("HuggingFace kimlik doğrulaması yapılamadı.")
        
        # Tüm modelleri listele
        available_models = list_available_models()
        
        if models_to_download is None or len(models_to_download) == 0:
            # Tüm modeller
            models_to_download = list(available_models.keys())
        
        # Belirtilen modellerin varlığını kontrol et
        for model_id in models_to_download[:]:
            if model_id not in available_models:
                logger.error(f"Model bulunamadı: {model_id}")
                models_to_download.remove(model_id)
        
        # Model yoksa çık
        if not models_to_download:
            logger.error("İndirilecek model bulunamadı.")
            return False
        
        total_models = len(models_to_download)
        logger.info(f"İndirilecek model sayısı: {total_models}")
        
        # Diffusers ve transformers kütüphanelerini yükle
        try:
            from diffusers import StableDiffusionPipeline
            from transformers import CLIPTextModel
        except ImportError:
            logger.error("diffusers ve transformers kütüphaneleri yüklü değil.")
            logger.error("Lütfen şu komutu çalıştırın: pip install diffusers transformers")
            return False
        
        # Modelleri indir
        for idx, model_id in enumerate(models_to_download):
            model_info = available_models[model_id]
            logger.info(f"Model indiriliyor ({idx+1}/{total_models}): {model_info['name']} ({model_id})")
            
            try:
                pipe = StableDiffusionPipeline.from_pretrained(model_info["repo"])
                logger.info(f"✓ Model başarıyla indirildi: {model_id}")
            except Exception as e:
                logger.error(f"Model indirilemedi: {model_id}, Hata: {e}")
        
        # LoRA adaptasyonlarını indir
        loras = list_available_loras()
        if loras:
            total_loras = len(loras)
            logger.info(f"İndirilecek LoRA sayısı: {total_loras}")
            
            for idx, (lora_id, lora_info) in enumerate(loras.items()):
                logger.info(f"LoRA indiriliyor ({idx+1}/{total_loras}): {lora_info['name']} ({lora_id})")
                try:
                    result = download_lora(lora_id)
                    if result:
                        logger.info(f"✓ LoRA başarıyla indirildi: {lora_id}")
                    else:
                        logger.error(f"LoRA indirilemedi: {lora_id}")
                except Exception as e:
                    logger.error(f"LoRA indirme hatası: {lora_id}, {e}")
        
        return True
    
    except Exception as e:
        logger.exception(f"Model indirme işlemi sırasında bir hata oluştu: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Model İndirme Aracı")
    parser.add_argument("--model", "-m", type=str, nargs="+", help="İndirilecek model ID'leri (boş bırakılırsa tüm modeller indirilir)")
    parser.add_argument("--auth", "-a", action="store_true", help="HuggingFace kimlik doğrulama kullan")
    parser.add_argument("--token", "-t", type=str, help="HuggingFace API token (kullanıcı arayüzünden alınabilir)")
    args = parser.parse_args()
    
    print("=" * 50)
    print("     AI Görsel Oluşturma - Model İndirme Aracı")
    print("=" * 50)
    
    # GPU bilgilerini kontrol et
    has_gpu, gpu_name, gpu_memory = check_gpu_info()
    
    # Disk alanını kontrol et
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    Path(models_dir).mkdir(exist_ok=True, parents=True)
    verify_disk_space(models_dir)
    
    # Modelleri indir
    success = download_models(
        models_to_download=args.model,
        models_dir=models_dir,
        use_auth=args.auth,
        hf_token=args.token
    )
    
    # Sonucu bildir
    if success:
        print("\n" + "=" * 50)
        print("Model indirme işlemi tamamlandı!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("Model indirme işlemi başarısız oldu.")
        print("Lütfen log dosyasını kontrol edin: model_download.log")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()
