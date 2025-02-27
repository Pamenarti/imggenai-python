import torch
import gc
import os
import time  # Eksik import eklendi
import logging
from PIL import Image
import numpy as np
from model_manager import load_model, get_prompt_suggestions, apply_lora_to_prompt, download_lora

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bellek optimizasyonu için yardımcı fonksiyonlar
def free_gpu_memory():
    """GPU belleğini temizle"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    gc.collect()

# Torch bellek optimizasyonları
def optimize_torch_for_device():
    """Çalıştığı cihaza göre torch ayarlarını optimize et"""
    if torch.cuda.is_available():
        # GPU bellek optimizasyonu
        torch.backends.cudnn.benchmark = True
        # Bellek tahsis stratejisini değiştir
        if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
            torch.cuda.set_per_process_memory_fraction(0.8)  # GPU belleğinin %80'ini kullan
        # Deterministik olmayan algoritmalar daha hızlıdır
        torch.use_deterministic_algorithms(False)
    else:
        # CPU optimizasyonları
        torch.set_num_threads(os.cpu_count())  # Tüm CPU çekirdeklerini kullan

# Metin açıklamasından görsel üret
def generate_image_from_text(
    prompt, 
    guidance_scale=7.5, 
    num_steps=50, 
    width=512, 
    height=512, 
    seed=None,
    model_id=None,
    lora_id=None,
    low_memory=False,
    debug=False
):
    """
    Metin açıklamasından görsel oluşturur
    
    Args:
        prompt (str): Görsel açıklaması
        guidance_scale (float): Classifier-Free Guidance (CFG) değeri
        num_steps (int): Diffusion adımı sayısı
        width (int): Görsel genişliği (512 veya 768 önerilir)
        height (int): Görsel yüksekliği (512 veya 768 önerilir)
        seed (int): Rastgele sayı üreteci tohumu (yinelenebilirlik için)
        model_id (str): Kullanılacak model ID'si
        lora_id (str): Kullanılacak LoRA ID'si (opsiyonel)
        low_memory (bool): Düşük bellek modu
        debug (bool): Debug modu açık mı?
        
    Returns:
        PIL.Image: Oluşturulan görsel
    """
    try:
        start_time = time.time()
        logger.info(f"Görsel oluşturuluyor: '{prompt}'")

        # Cihaz belirleme - GPU yoksa CPU kullan
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # İlerlemeyi logla
        logger.info(f"Model yükleniyor: {model_id if model_id else 'default'} - Cihaz: {device}")
        
        # Modeli yükle
        pipe = load_model(model_id, device, safety_checker=True, low_memory=low_memory)
        
        if pipe is None:
            logger.error("Model yüklenemedi")
            return None
        
        # LoRA adaptasyonu ekle
        if lora_id:
            try:
                logger.info(f"LoRA uygulanıyor: {lora_id}")
                lora_path = download_lora(lora_id)
                if lora_path:
                    # LoRA yükleme mümkünse
                    if hasattr(pipe, "load_lora_weights"):
                        pipe.load_lora_weights(lora_path)
                        logger.info("LoRA başarıyla uygulandı")
                    else:
                        logger.warning("Bu model doğrudan LoRA yüklemeyi desteklemiyor")
                    
                    # Prompt'a LoRA tetikleyicilerini ekle
                    prompt = apply_lora_to_prompt(prompt, lora_id)
            except Exception as e:
                logger.error(f"LoRA uygulama hatası: {e}")
        
        # Rastgele tohum değeri
        if seed is not None:
            generator = torch.Generator(device=device).manual_seed(seed)
        else:
            generator = torch.Generator(device=device).manual_seed(int(torch.randint(0, 2147483647, (1,)).item()))
        
        if debug:
            logger.debug(f"Parametreler: model={model_id}, adımlar={num_steps}, guidance={guidance_scale}")
        
        # Görseli oluştur
        # Bellek optimizasyonu için torch.cuda.amp.autocast() kullan
        with torch.inference_mode():
            # GPU varsa, low_memory modunda önbellek boşaltma
            if device == "cuda" and low_memory:
                torch.cuda.empty_cache()
            
            # DiffusionPipeline çağır
            result = pipe(
                prompt=prompt,
                guidance_scale=guidance_scale,
                num_inference_steps=num_steps,
                width=width,
                height=height,
                generator=generator
            )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Görsel oluşturuldu: {elapsed_time:.2f} saniye")
        
        # NSFW denetimi - result.nsfw_content_detected None değilse
        if hasattr(result, "nsfw_content_detected") and result.nsfw_content_detected is not None:
            try:
                # İterasyon yapmadan önce gerçekten iterable olduğunu kontrol et
                if isinstance(result.nsfw_content_detected, (list, tuple)) and any(result.nsfw_content_detected):
                    logger.warning("NSFW içerik tespit edildi, görsel blurlanabilir")
            except Exception as e:
                logger.debug(f"NSFW denetimi sırasında hata: {e}")
        
        # Görüntüyü döndür
        if result and hasattr(result, "images") and isinstance(result.images, (list, tuple)) and len(result.images) > 0:
            return result.images[0]
        else:
            if debug:
                logger.debug("Result yapısı: " + str(type(result)))
                if result and hasattr(result, "images"):
                    logger.debug(f"Images tipi: {type(result.images)}")
            return None
        
    except Exception as e:
        logger.error(f"Görsel oluşturma hatası: {e}", exc_info=debug)
        return None

# Doğrudan çalıştırma testi
if __name__ == "__main__":
    test_prompt = "A beautiful mountain landscape with a lake, photorealistic, high resolution"
    image = generate_image_from_text(test_prompt, num_steps=30, debug=True)
    
    if image:
        image.save("test_output.png")
        print("Test görseli oluşturuldu: test_output.png")
    else:
        print("Görsel oluşturulamadı")

def enrich_prompt(prompt):
    """Prompta kalite arttırıcı anahtar kelimeler ekle"""
    # Kullanıcı zaten detaylı bir prompt vermişse değiştirme
    if len(prompt.split()) > 10:
        return prompt
        
    quality_suffix = ", 8k yüksek çözünürlük, ayrıntılı, yüksek kalite, mükemmel aydınlatma, profesyonel fotoğraf"
    
    # Eğer anahtar kelimeler zaten promptta varsa ekleme yapma
    quality_keywords = ["8k", "yüksek çözünürlük", "ayrıntılı", "yüksek kalite"]
    if any(keyword in prompt.lower() for keyword in quality_keywords):
        return prompt
        
    return prompt + quality_suffix
