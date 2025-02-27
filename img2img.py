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
                image=init_image,
                strength=strength,
                guidance_scale=guidance_scale,
                negative_prompt=negative_prompt,
                num_inference_steps=num_steps
            )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Görsel dönüştürme tamamlandı: {elapsed_time:.2f} saniye")
        
        # NSFW kontrolü
        if hasattr(result, "nsfw_content_detected") and result.nsfw_content_detected is not None:
            if any(result.nsfw_content_detected):
                logger.warning("NSFW içerik tespit edildi, görsel blurlanabilir")
        
        # Sonucu döndür
        if result and hasattr(result, "images") and len(result.images) > 0:
            return result.images[0]
        else:
            logger.warning("Görsel dönüştürme başarısız oldu, sonuç bulunamadı")
            return None
            
    except Exception as e:
        logger.error(f"Görsel dönüştürülürken hata: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    # Test
    test_input = Image.new("RGB", (512, 512), color="white")
    result_image = generate_image_from_image(
        test_input, 
        "A beautiful mountain landscape, photorealistic", 
        strength=0.8
    )
    
    if result_image:
        result_image.save("img2img_test_output.png")
        print("Test başarılı, sonuç kaydedildi: img2img_test_output.png")
    else:
        print("Test başarısız")
