import os
import torch
import logging
from PIL import Image
import numpy as np
from txt2img import generate_image_from_text
from img2img import generate_image_from_image
from model_manager import list_available_models, list_available_loras

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_workflow(prompt, workflow_type="Basit"):
    """
    Çeşitli AI görüntü oluşturma iş akışlarını çalıştırır
    
    Args:
        prompt: Temel metin açıklaması
        workflow_type: İş akışı türü ("Basit", "Stil Transferi", "Gelişmiş Düzenleme")
        
    Returns:
        Oluşturulan görsellerin listesi
    """
    try:
        logger.info(f"İş akışı başlatılıyor: {workflow_type}")
        
        if workflow_type == "Basit":
            return run_simple_workflow(prompt)
        elif workflow_type == "Stil Transferi":
            return run_style_transfer_workflow(prompt)
        elif workflow_type == "Gelişmiş Düzenleme":
            return run_advanced_editing_workflow(prompt)
        else:
            logger.error(f"Tanımlanamayan iş akışı türü: {workflow_type}")
            return []
            
    except Exception as e:
        logger.exception(f"İş akışı hatası: {e}")
        return []

def run_simple_workflow(prompt):
    """Basit bir iş akışı - sadece tek bir görsel üretir"""
    logger.info(f"Basit iş akışı: {prompt}")
    
    # Farklı modelleri dene
    images = []
    models = list(list_available_models().keys())
    
    # İlk iki modeli kullan (varsayılan ve pony-realism)
    for model_id in models[:2]:
        try:
            image = generate_image_from_text(
                prompt=prompt,
                guidance_scale=7.5,
                num_steps=40,
                model_id=model_id
            )
            
            if image:
                images.append(image)
                
        except Exception as e:
            logger.error(f"{model_id} modeliyle görsel oluşturma hatası: {e}")
    
    return images

def run_style_transfer_workflow(prompt):
    """
    Stil transferi iş akışı - farklı sanatsal stillerde görseller üretir
    """
    logger.info(f"Stil transferi iş akışı: {prompt}")
    
    # Sanatsal stiller
    styles = [
        "oil painting style",
        "anime style",
        "digital art style",
        "watercolor style",
        "pencil sketch style"
    ]
    
    images = []
    
    # Her stil için bir görsel oluştur
    for style in styles:
        styled_prompt = f"{prompt}, {style}, high quality"
        
        try:
            # Her stilin hangi modele daha uygun olduğunu belirle
            if "anime" in style or "digital" in style:
                model_id = "flux-uncensored"
            else:
                model_id = "pony-realism-v21"
                
            image = generate_image_from_text(
                prompt=styled_prompt,
                guidance_scale=7.5,
                num_steps=35,
                model_id=model_id
            )
            
            if image:
                images.append(image)
                
        except Exception as e:
            logger.error(f"Stil transferi hatası ({style}): {e}")
    
    return images

def run_advanced_editing_workflow(prompt):
    """
    Gelişmiş düzenleme iş akışı - bir görsel oluşturup sonra onu dönüştürür
    """
    logger.info(f"Gelişmiş düzenleme iş akışı: {prompt}")
    
    images = []
    
    try:
        # 1. Temel görseli oluştur
        base_image = generate_image_from_text(
            prompt=prompt,
            guidance_scale=7.5,
            num_steps=30,
            model_id="pony-realism-v22"
        )
        
        if not base_image:
            logger.error("Temel görsel oluşturulamadı")
            return images
            
        images.append(base_image)
        
        # 2. Görseli farklı şekillerde dönüştür
        variations = [
            "add more details, increase contrast", 
            "dramatic lighting",
            "bright colors, cinematic shot",
            "dark mood, dramatic shadows"
        ]
        
        for var in variations:
            try:
                modified = generate_image_from_image(
                    init_image=base_image,
                    prompt=f"{prompt}, {var}",
                    strength=0.5,
                    num_steps=25
                )
                
                if modified:
                    images.append(modified)
                    
            except Exception as e:
                logger.error(f"Varyasyon oluşturma hatası ({var}): {e}")
        
        # 3. Görsele LoRA uygula (eğer uygunsa)
        if "character" in prompt.lower() or "portrait" in prompt.lower():
            loras = list_available_loras()
            if "tatsumaki-opm" in loras:
                try:
                    lora_image = generate_image_from_text(
                        prompt=prompt,
                        guidance_scale=7.5,
                        num_steps=30,
                        model_id="flux-uncensored",
                        lora_id="tatsumaki-opm"
                    )
                    
                    if lora_image:
                        images.append(lora_image)
                        
                except Exception as e:
                    logger.error(f"LoRA uygulama hatası: {e}")
        
    except Exception as e:
        logger.exception(f"Gelişmiş düzenleme hatası: {e}")
    
    return images

# Test için
if __name__ == "__main__":
    test_prompt = "a beautiful mountain landscape with lake and sunset"
    results = run_workflow(test_prompt, "Basit")
    print(f"{len(results)} görsel oluşturuldu")
