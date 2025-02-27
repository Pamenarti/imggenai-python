#!/usr/bin/env python3
"""
Bu script, AI Görsel Oluşturma sistemi için yapılandırılmış modelleri test eder.
Her modeli yükler ve basit bir görsel oluşturma testi yapar.
"""

import os
import torch
import argparse
import logging
from PIL import Image
import time
from datetime import datetime
from pathlib import Path
from model_manager import (
    list_available_models, 
    load_model, 
    list_available_loras
)

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("model_test.log")
    ]
)
logger = logging.getLogger(__name__)

def test_gpu():
    """GPU durumunu kontrol et ve bilgilerini yazdır"""
    print("\n==== GPU Bilgileri ====")
    
    if not torch.cuda.is_available():
        print("❌ CUDA destekli GPU bulunamadı. Testler CPU üzerinde yapılacak.")
        return False
    
    device_count = torch.cuda.device_count()
    print(f"✅ {device_count} CUDA GPU bulundu.")
    
    for i in range(device_count):
        device_name = torch.cuda.get_device_name(i)
        device_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
        print(f"GPU {i}: {device_name} ({device_mem:.2f} GB)")
    
    return True

def test_model(model_id, prompt="a beautiful landscape with mountains", output_dir="test_outputs"):
    """Belirli bir modeli test et ve örnek görsel oluştur"""
    logger.info(f"'{model_id}' modeli test ediliyor...")
    
    try:
        # Çıktı dizinini oluştur
        os.makedirs(output_dir, exist_ok=True)
        
        # Modeli yükle
        start_time = time.time()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = load_model(model_id=model_id, device=device)
        load_time = time.time() - start_time
        
        if pipe is None:
            logger.error(f"❌ '{model_id}' modeli yüklenemedi!")
            return False
        
        logger.info(f"✅ '{model_id}' modeli yüklendi ({load_time:.2f} saniye)")
        
        # Test görseli oluştur
        logger.info(f"Örnek prompt ile görsel oluşturuluyor: '{prompt}'")
        start_time = time.time()
        
        # Görsel oluştur
        with torch.inference_mode():
            result = pipe(
                prompt=prompt,
                guidance_scale=7.5,
                num_inference_steps=20  # Test için düşük tutuyoruz
            )
        
        gen_time = time.time() - start_time
        
        # Görsel dosyasını kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{output_dir}/{model_id.replace('/', '_')}_{timestamp}.png"
        result.images[0].save(output_filename)
        
        logger.info(f"✅ Görsel oluşturuldu ({gen_time:.2f} saniye)")
        logger.info(f"✅ Dosya kaydedildi: {output_filename}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ '{model_id}' modeli test edilirken hata oluştu: {e}")
        return False

def test_all_models(prompt="an astronaut riding a horse on mars", output_dir="test_outputs"):
    """Tüm yapılandırılmış modelleri test et"""
    print("\n==== Model Testleri ====")
    
    # Modelleri listele
    models = list_available_models()
    total_models = len(models)
    
    print(f"Toplam {total_models} model test edilecek.")
    
    # Sonuç tablosu için değişkenler
    results = {
        "success": [],
        "failed": []
    }
    
    # Her modeli test et
    for idx, (model_id, model_info) in enumerate(models.items()):
        print(f"\n[{idx+1}/{total_models}] {model_info['name']} ({model_id}) testi:")
        success = test_model(model_id, prompt, output_dir)
        
        if success:
            results["success"].append(model_id)
            print(f"✅ '{model_id}' başarıyla test edildi.")
        else:
            results["failed"].append(model_id)
            print(f"❌ '{model_id}' testi başarısız oldu.")
    
    # LoRA'ları listele
    loras = list_available_loras()
    if loras:
        print(f"\nSistemde {len(loras)} LoRA adaptasyonu yapılandırılmış (ayrı test edilmedi)")
    
    # Sonuçları yazdır
    print("\n==== Test Sonuçları ====")
    print(f"Toplam Model Sayısı: {total_models}")
    print(f"Başarılı: {len(results['success'])}")
    print(f"Başarısız: {len(results['failed'])}")
    
    if results["failed"]:
        print("\nBaşarısız modeller:")
        for model_id in results["failed"]:
            print(f"- {model_id}")
    
    return results

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="AI Görsel Oluşturma Model Test Aracı")
    parser.add_argument("--model", "-m", type=str, help="Test edilecek belirli bir model ID'si")
    parser.add_argument("--prompt", "-p", type=str, default="a beautiful landscape with mountains", help="Test için kullanılacak prompt")
    parser.add_argument("--output", "-o", type=str, default="test_outputs", help="Test görsellerinin kaydedileceği dizin")
    args = parser.parse_args()
    
    print("=" * 50)
    print("AI Görsel Oluşturma - Model Test Aracı")
    print("=" * 50)
    
    # GPU durumunu kontrol et
    has_gpu = test_gpu()
    if not has_gpu:
        print("⚠️ GPU bulunamadı, testler CPU üzerinde yapılacak ve yavaş olabilir.")
    
    # Çıktı dizinini oluştur
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Belirli bir model test edilecek mi?
    if args.model:
        models = list_available_models()
        if args.model in models:
            test_model(args.model, args.prompt, args.output)
        else:
            print(f"❌ '{args.model}' modeli bulunamadı!")
            print("\nKullanılabilir modeller:")
            for model_id, model_info in models.items():
                print(f"- {model_id}: {model_info['name']}")
    else:
        # Tüm modelleri test et
        test_all_models(args.prompt, args.output)
    
    print("\nTest işlemi tamamlandı!")

if __name__ == "__main__":
    main()
