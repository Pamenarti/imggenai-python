import torch
import numpy as np
from PIL import Image
import logging
from model_manager import load_img2img_model, apply_lora_to_prompt, download_lora

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Görselden görsel oluştur
def generate_image_from_image(init_image, prompt, strength=0.8, num_steps=50, model_id=None, lora_id=None, low_memory=False):
    """
    Bir kaynak görselden yeni bir görsel oluşturur
    
    Args:
        init_image: Kaynak görsel
        prompt: Metin açıklaması
        strength: Değişim miktarı (0.0 - 1.0)
        num_steps: Diffusion adım sayısı
        model_id: Kullanılacak model kimliği
        lora_id: Kullanılacak LoRA adaptasyonu
        low_memory: Düşük bellek modu
    """
    try:
        if init_image is None:
            return None
            
        logger.info(f"Görsel dönüştürülüyor: '{prompt}', strength={strength}")
        
        # Cihaz seçimi
        device = "cuda" if torch.cuda.is_available() else "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu"
        
        # Image2Image modelini yükle
        pipe = load_img2img_model(model_id=model_id, device=device, safety_checker=False, low_memory=low_memory)
        
        if pipe is None:
            logger.error("Model yüklenemedi!")
            return Image.new('RGB', (512, 512), color='red')
        
        # Görseli standart boyuta getir
        init_image = init_image.resize((768, 512))
        
        # Prompt'u zenginleştir
        enriched_prompt = enrich_img2img_prompt(prompt)
        
        # LoRA kullanılıyorsa prompt'u güncelle
        if lora_id:
            download_lora(lora_id)  # LoRA'yı indir (eğer yoksa)
            enriched_prompt = apply_lora_to_prompt(enriched_prompt, lora_id)
        
        try:
            # Görseli oluştur
            with torch.inference_mode():
                result = pipe(
                    prompt=enriched_prompt,
                    image=init_image,
                    strength=strength,
                    num_inference_steps=int(num_steps)
                )
            
            image = result.images[0]
            logger.info("Görsel dönüştürme başarılı")
            return image
            
        except torch.cuda.OutOfMemoryError:
            logger.warning("GPU bellek yetersiz, düşük bellek modu deneniyor...")
            
            # Belleği temizle
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Daha küçük boyutta dene
            small_image = init_image.resize((512, 384))
            
            # Daha düşük parametrelerle tekrar dene
            with torch.inference_mode():
                result = pipe(
                    prompt=enriched_prompt,
                    image=small_image,
                    strength=strength,
                    num_inference_steps=min(int(num_steps), 30)
                )
            
            return result.images[0]
    
    except Exception as e:
        logger.exception(f"Görsel dönüştürme hatası: {e}")
        return Image.new('RGB', (512, 512), color='gray')

def enrich_img2img_prompt(prompt):
    """Image2Image için prompt zenginleştirme"""
    quality_keywords = ["yüksek detay", "8k", "yüksek kalite"]
    
    # Eğer promp zaten yeterince detaylı ise değiştirme
    if len(prompt.split()) > 8 or any(keyword in prompt.lower() for keyword in quality_keywords):
        return prompt
        
    return prompt + ", yüksek detay, 8k çözünürlük"
