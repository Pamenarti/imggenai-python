import torch
import time
import logging
from PIL import Image
from model_manager import load_img2img_model

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_image_from_image(
    init_image, 
    prompt, 
    strength=0.8, 
    guidance_scale=7.5, 
    num_steps=50,
    model_id=None,
    negative_prompt="",
    low_memory=False
):
    """
    Var olan bir görselden yeni bir görsel oluşturur (img2img)
    
    Args:
        init_image (PIL.Image): Başlangıç görseli
        prompt (str): İstenen değişiklik için metin açıklaması
        strength (float): Değişim miktarı (0.0-1.0 arası, 1.0 tamamen yeni görsele yaklaşır)
        guidance_scale (float): Prompt'a ne kadar sadık olunacağı (CFG)
        num_steps (int): Diffusion adımı sayısı
        model_id (str): Kullanılacak model ID'si
        negative_prompt (str): İstenmeyen özelliklerin belirtildiği metin
        low_memory (bool): Düşük bellek modu aktif mi?
        
    Returns:
        PIL.Image: Oluşturulan görsel
    """
    try:
        start_time = time.time()
        logger.info(f"Görsel dönüştürülüyor: '{prompt}'")
        
        # Cihaz belirleme
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Img2img pipeline'ı yükle
        pipe = load_img2img_model(model_id, device, safety_checker=True, low_memory=low_memory)
        
        if pipe is None:
            logger.error("Img2img modeli yüklenemedi")
            return None
        
        # Görseli oluştur
        with torch.inference_mode():
            # GPU varsa ve low_memory modundaysa önbellek temizle
            if device == "cuda" and low_memory:
                torch.cuda.empty_cache()
            
            # Oluşturma işlemi
            result = pipe(
                prompt=prompt,
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
