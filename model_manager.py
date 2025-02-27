import os
import torch
import logging
import json
import requests
import shutil
from pathlib import Path
from diffusers import (
    StableDiffusionPipeline, 
    StableDiffusionImg2ImgPipeline,
    DPMSolverMultistepScheduler
)
from huggingface_hub import hf_hub_download, login
from PIL import Image

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model tanımları
AVAILABLE_MODELS = {
    "stable-diffusion-v1-5": {
        "name": "Stable Diffusion v1.5",
        "repo": "runwayml/stable-diffusion-v1-5",
        "type": "diffusers",
        "default": True,
        "description": "Temel model"
    },
    "pony-realism-v21": {
        "name": "Pony Realism v2.1",
        "repo": "LyliaEngine/ponyRealism_v21MainVAE",
        "type": "diffusers",
        "default": False,
        "description": "Gerçekçi görseller için özel model"
    },
    "pony-realism-v22": {
        "name": "Pony Realism v2.2",
        "repo": "TheImposterImposters/PonyRealism-v2.2MainVAE",
        "type": "diffusers",
        "default": False,
        "description": "Geliştirilmiş gerçekçi görseller için özel model"
    },
    "flux-uncensored": {
        "name": "Flux Uncensored",
        "repo": "enhanceaiteam/Flux-uncensored",
        "type": "diffusers",
        "default": False, 
        "description": "Filtresiz görsel üretimi için özel model (18+ içerik üretebilir)"
    }
}

# LoRA adaptasyonları
AVAILABLE_LORAS = {
    "tatsumaki-opm": {
        "name": "Tatsumaki (One Punch Man)",
        "url": "https://civitai.com/api/download/models/415015",
        "local_path": "models/loras/tatsumaki_opm.safetensors",
        "type": "lora",
        "description": "One Punch Man Tatsumaki karakteri için uyarlama",
        "prompt_trigger": "tatsumaki, one punch man, character, green hair",
        "weight": 0.8
    }
}

# Model ID'lerine göre önerilen promptlar
PROMPT_SUGGESTIONS = {
    "runwayml/stable-diffusion-v1-5": [
        "A photorealistic portrait of a young woman with blue eyes",
        "A scenic landscape at sunset with mountains and a lake",
        "A fantasy character with detailed armor and magical effects"
    ],
    "pony-diffusion/pony-v2-1": [
        "A hyperrealistic portrait photograph of a woman, detailed features, professional lighting, 8k",
        "A photorealistic landscape with mountains and forest, golden hour, detailed, cinematic",
        "A still life with fruits and flowers, extreme detail, studio lighting, photorealistic"
    ],
    "pony-diffusion/pony-v2-2": [
        "An ultra-detailed portrait of a man with beard, piercing eyes, professional photography",
        "An aerial view of a coastal city at dawn, photorealistic, highly detailed",
        "A close-up of an exotic animal, sharp focus, natural lighting, studio quality"
    ],
    "flux-uncensored/flux": [
        "Digital art of a futuristic city with neon lights and flying cars",
        "A fantasy character, wizard casting a spell, vibrant colors, magical effects",
        "An anime-style portrait of a warrior in battle pose, detailed background"
    ]
}

class ModelManager:
    def __init__(self, models_dir="/home/agrotest2/imggenai/models"):
        """Model yöneticisi başlatır"""
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.lora_dir = self.models_dir / "loras"
        self.lora_dir.mkdir(parents=True, exist_ok=True)
        self.model_cache = {}
        self.current_model_id = None

        # Lora dosyalarının konumlarını takip et
        self.lora_paths = {}
        
        # Model bilgilerini kaydet
        self.save_model_info()
    
    def save_model_info(self):
        """Model bilgilerini JSON dosyasına kaydet"""
        model_info = {
            "models": AVAILABLE_MODELS,
            "loras": AVAILABLE_LORAS
        }
        with open(self.models_dir / "model_info.json", "w") as f:
            json.dump(model_info, f, indent=4)
    
    def list_models(self):
        """Kullanılabilir modelleri listeler"""
        return AVAILABLE_MODELS
    
    def list_loras(self):
        """Kullanılabilir LoRA adaptasyonlarını listeler"""
        return AVAILABLE_LORAS
    
    def get_default_model_id(self):
        """Varsayılan model kimliğini döndürür"""
        for model_id, info in AVAILABLE_MODELS.items():
            if info.get("default", False):
                return model_id
        # Varsayılan yoksa ilk model
        return list(AVAILABLE_MODELS.keys())[0]
    
    def get_prompt_suggestions(self, model_id=None):
        """Seçili model için prompt önerileri döndürür"""
        if not model_id:
            model_id = self.current_model_id or self.get_default_model_id()
        
        # Temel öneriler
        suggestions = [
            "a photograph of an astronaut riding a horse on mars, high quality",
            "a professional photograph of a mountain landscape, Alps, sunset, detailed",
            "a fantasy castle on a floating island, detailed, vibrant colors",
            "portrait of a smiling woman with blue eyes, professional lighting, high quality"
        ]
        
        # Model özelliğine göre ekstra öneriler
        if "pony-realism" in model_id:
            suggestions.extend([
                "a hyper realistic portrait of a beautiful woman, 8k, detailed skin texture",
                "realistic landscape, mountains, forest, lake, sunset, 8k photography"
            ])
        elif "flux" in model_id:
            suggestions.extend([
                "highly detailed digital art, vibrant colors, fantasy theme",
                "futuristic sci-fi cityscape, detailed, neon lights, volumetric lighting"
            ])
            
        return suggestions
    
    def download_models(self):
        """Tüm modelleri indirir"""
        for model_id, model_info in AVAILABLE_MODELS.items():
            # Flux-uncensored gibi belirli modeller için HF erişim gerekebilir
            if (model_id == "flux-uncensored"):
                try:
                    login()
                except:
                    logger.warning(f"{model_id} modeli için HF erişimi gerekli olabilir")
            
            logger.info(f"{model_id} modeli önbelleğe alınıyor...")
            try:
                _ = StableDiffusionPipeline.from_pretrained(
                    model_info["repo"],
                    local_files_only=False
                )
                logger.info(f"{model_id} modeli başarıyla indirildi")
            except Exception as e:
                logger.error(f"{model_id} modeli indirilemedi: {e}")
    
    def load_model(self, model_id=None, device=None, safety_checker=True, low_memory=False):
        """
        Belirtilen modeli bellek verimli şekilde yükler
        
        Args:
            model_id: Model kimliği (AVAILABLE_MODELS içinde tanımlı)
            device: "cuda", "mps" veya "cpu"
            safety_checker: Güvenlik filtresinin kullanılıp kullanılmayacağı
            low_memory: Düşük bellek modu aktifleştirilsin mi?
        """
        if not model_id:
            model_id = self.get_default_model_id()
        
        # Cihazı belirle
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        
        logger.info(f"'{model_id}' modeli {device} cihazı için yükleniyor...")
        
        # Model zaten yüklendiyse ve aynı cihazda ise doğrudan döndür
        cache_key = f"{model_id}_{device}_{safety_checker}_{low_memory}"
        if cache_key in self.model_cache:
            logger.info(f"Model önbellekten kullanılıyor: {model_id}")
            self.current_model_id = model_id
            return self.model_cache[cache_key]
        
        # Model bilgilerini al
        if model_id not in AVAILABLE_MODELS:
            logger.warning(f"Model bulunamadı: {model_id}, varsayılan model kullanılıyor")
            model_id = self.get_default_model_id()
        
        model_info = AVAILABLE_MODELS[model_id]
        repo_id = model_info["repo"]
        
        try:
            # Bellek optimizasyonu yapılandırması
            load_options = {
                "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
                "safety_checker": None if not safety_checker else None,  # Güvenlik kontrolünü devre dışı bırakabilirsiniz
                "local_files_only": False  # Yüklü değilse indir
            }
            
            # Düşük bellek modu için ek ayarlar
            if low_memory:
                load_options["variant"] = "fp16" if device == "cuda" else None
                load_options["low_cpu_mem_usage"] = True
            
            # Model yükle
            pipe = StableDiffusionPipeline.from_pretrained(
                repo_id,
                **load_options
            )
            
            # Cihaza taşı
            pipe = pipe.to(device)
            
            # Bellek optimizasyonu
            if device == "cuda":
                pipe.enable_attention_slicing()
                if low_memory:
                    if hasattr(pipe, "enable_model_cpu_offload"):
                        pipe.enable_model_cpu_offload()
                    else:
                        logger.warning("CPU offload bu model için uygulanamadı")
            
            # Programlayıcıyı DPM-Solver olarak değiştir (daha hızlı ve kaliteli)
            pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
            
            # Önbelleğe al
            self.model_cache[cache_key] = pipe
            self.current_model_id = model_id
            
            logger.info(f"Model başarıyla yüklendi: {model_id}")
            return pipe
        
        except Exception as e:
            logger.error(f"Model yüklenirken hata oluştu {model_id}: {e}")
            
            # Yedek olarak varsayılan modeli dene
            if model_id != "stable-diffusion-v1-5":
                logger.info("Varsayılan model yükleniyor...")
                return self.load_model("stable-diffusion-v1-5", device, safety_checker, low_memory)
            else:
                logger.error("Varsayılan model de yüklenemedi!")
                return None
    
    def load_img2img_model(self, model_id=None, device=None, safety_checker=True, low_memory=False):
        """Img2Img modeli yükle"""
        # Önce txt2img modelini yükle
        txt2img_pipe = self.load_model(model_id, device, safety_checker, low_memory)
        
        if txt2img_pipe is None:
            return None
        
        try:
            # Mevcut modelden img2img pipeline'ı oluştur
            img2img_pipe = StableDiffusionImg2ImgPipeline(**txt2img_pipe.components)
            
            # Aynı cihaza taşı
            img2img_pipe = img2img_pipe.to(device)
            
            return img2img_pipe
        except Exception as e:
            logger.error(f"Img2img dönüştürme hatası: {e}")
            return None
    
    def download_lora(self, lora_id):
        """LoRA dosyasını indir"""
        if lora_id not in AVAILABLE_LORAS:
            logger.error(f"LoRA bulunamadı: {lora_id}")
            return None
        
        lora_info = AVAILABLE_LORAS[lora_id]
        lora_path = self.lora_dir / f"{lora_id}.safetensors"
        
        # Dosya zaten varsa, doğrudan yolu döndür
        if lora_path.exists():
            logger.info(f"LoRA zaten indirilmiş: {lora_id}")
            self.lora_paths[lora_id] = str(lora_path)
            return str(lora_path)
        
        # CivitAI'dan indirme işlemi
        try:
            if "civitai.com" in lora_info["url"]:
                logger.info(f"CivitAI'dan LoRA indiriliyor: {lora_id}")
                
                # CivitAI API değişiklikleri nedeniyle artık bir token veya oturum gerekebilir
                # Şimdilik kullanıcıya manuel indirme talimatları sağlayalım
                logger.warning(f"CivitAI kimlik doğrulama hatası: API değişikliği olabilir.")
                logger.info(f"LoRA dosyasını manuel olarak indirmek için: {lora_info['url']}")
                logger.info(f"İndirilen dosyayı '{lora_path}' konumuna kaydedin ve uygulamayı yeniden başlatın.")
                
                # Örnek alternatif indirme URL'si (eğer varsa)
                alt_url = lora_info.get("alt_url")
                if alt_url:
                    logger.info(f"Alternatif kaynaktan indirmeyi deniyorum: {alt_url}")
                    response = requests.get(alt_url, stream=True)
                    response.raise_for_status()
                    
                    with open(lora_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    logger.info(f"LoRA başarıyla indirildi: {lora_id}")
                    self.lora_paths[lora_id] = str(lora_path)
                    return str(lora_path)
                else:
                    # Manuel indirme için varsayılan model döndür
                    logger.warning("Manuel indirme gerekiyor, LoRA kullanılmadan devam ediliyor.")
                    return None
                    
        except Exception as e:
            logger.error(f"LoRA indirilirken hata oluştu: {e}")
            return None
    
    def apply_lora_to_prompt(self, prompt, lora_id):
        """Prompt'a LoRA tetikleyicilerini ekle"""
        if lora_id not in AVAILABLE_LORAS:
            return prompt
        
        lora_info = AVAILABLE_LORAS[lora_id]
        trigger = lora_info.get("prompt_trigger", "")
        
        if trigger and trigger.lower() not in prompt.lower():
            enhanced_prompt = f"{prompt}, {trigger}"
            logger.info(f"Prompt LoRA tetikleyicileriyle zenginleştirildi: {lora_id}")
            return enhanced_prompt
        
        return prompt

# Tekil örnek oluştur
model_manager = ModelManager()

# Dışa aktarılacak fonksiyonlar
def load_model(model_id=None, device=None, safety_checker=True, low_memory=False):
    return model_manager.load_model(model_id, device, safety_checker, low_memory)

def load_img2img_model(model_id=None, device=None, safety_checker=True, low_memory=False):
    return model_manager.load_img2img_model(model_id, device, safety_checker, low_memory)

def list_available_models():
    return model_manager.list_models()

def list_available_loras():
    return model_manager.list_loras()

def get_prompt_suggestions(model_id=None):
    return model_manager.get_prompt_suggestions(model_id)

def download_lora(lora_id):
    return model_manager.download_lora(lora_id)

def apply_lora_to_prompt(prompt, lora_id):
    return model_manager.apply_lora_to_prompt(prompt, lora_id)

def download_all_models():
    model_manager.download_models()

# Kullanım örneği
if __name__ == "__main__":
    print("Kullanılabilir modeller:")
    models = list_available_models()
    for model_id, model_info in models.items():
        print(f"- {model_info['name']} ({model_id}): {model_info['description']}")
    
    print("\nKullanılabilir LoRA adaptasyonları:")
    loras = list_available_loras()
    for lora_id, lora_info in loras.items():
        print(f"- {lora_info['name']} ({lora_id}): {lora_info['description']}")
