import os
import json
import torch
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def get_models_registry():
    """Kayıtlı modellerin listesini al"""
    registry_path = Path(os.path.expanduser("~/.cache/imggenai/models_registry.json"))
    
    if not registry_path.exists():
        logger.warning(f"Model kayıt dosyası bulunamadı: {registry_path}")
        return {
            "checkpoints": [],
            "loras": [],
            "embeddings": [],
            "controlnet": []
        }
    
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_available_models():
    """Kullanılabilir modellerin listesini döndür"""
    registry = get_models_registry()
    
    models = {
        "checkpoints": [model["name"] for model in registry["checkpoints"]],
        "loras": [model["name"] for model in registry["loras"]],
        "embeddings": [model["name"] for model in registry["embeddings"]],
        "controlnet": [model["name"] for model in registry["controlnet"]]
    }
    
    return models

def get_model_path(model_name, model_type="checkpoint"):
    """Model adına göre dosya yolunu döndür"""
    registry = get_models_registry()
    
    models = registry.get(f"{model_type}s", [])
    for model in models:
        if model["name"].lower() == model_name.lower():
            return model["path"]
    
    return None

def apply_lora_to_pipeline(pipeline, lora_path, alpha=0.75):
    """Stable Diffusion pipeline'a LoRA modelini uygula"""
    try:
        from diffusers import DiffusionPipeline
        import torch
        
        # LoRA'yı pipeline'a yükle
        if hasattr(pipeline, "load_lora_weights"):
            pipeline.load_lora_weights(lora_path, alpha=alpha)
            logger.info(f"LoRA modeli yüklendi: {os.path.basename(lora_path)}")
        else:
            logger.warning(f"Bu pipeline LoRA yüklemeyi desteklemiyor")
        
        return pipeline
    except Exception as e:
        logger.error(f"LoRA yüklemesi sırasında hata: {e}")
        return pipeline

def get_lora_prompt_additions(lora_name):
    """LoRA modeli için önerilen prompt eklemelerini döndür"""
    
    # Önerilen prompt eklemeleri
    lora_prompts = {
        "ponyRealismEnhancer": ["pony realism enhancer", "detailed equine features"],
        "backgroundDetailEnhancer": ["detailed background", "background enhancer", "high quality environment"],
        "tatsumakiOnePunch": ["tatsumaki", "one punch man style", "green hair", "psychic powers"]
    }
    
    # İsim normalizasyonu
    lora_name_normalized = ''.join(c for c in lora_name if c.isalnum())
    
    # Eşleşen prompt eklemelerini döndür
    for name, prompts in lora_prompts.items():
        if name.lower() in lora_name_normalized.lower():
            return prompts
    
    return []

def load_custom_model(model_name="ponyRealism"):
    """Özel bir Stable Diffusion modelini yükle"""
    try:
        from diffusers import StableDiffusionPipeline
        import torch
        
        model_path = get_model_path(model_name, "checkpoint")
        
        if not model_path:
            logger.warning(f"{model_name} modeli bulunamadı, varsayılan model kullanılacak")
            return None
        
        logger.info(f"{model_name} modeli yükleniyor: {model_path}")
        
        # Modeli yükle
        pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            use_safetensors=model_path.endswith(".safetensors")
        )
        
        # GPU'ya taşı
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
            pipe.enable_attention_slicing()
        
        logger.info(f"{model_name} modeli başarıyla yüklendi")
        return pipe
    
    except Exception as e:
        logger.error(f"Model yükleme hatası: {e}")
        logger.info("Varsayılan model kullanılacak")
        return None
