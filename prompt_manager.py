"""
Bu modül, farklı modeller için örnek promptları yönetir.
"""

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

def get_prompt_suggestions(model_id):
    """
    Belirtilen model ID'si için önerilen promptları döndürür.
    
    Args:
        model_id (str): Model ID'si
        
    Returns:
        list: Önerilen promptların listesi
    """
    # Belirtilen model ID'si için önerilen promptları döndür
    if model_id in PROMPT_SUGGESTIONS:
        return PROMPT_SUGGESTIONS[model_id]
    
    # Varsayılan promptları döndür
    return [
        "A photorealistic portrait of a young woman with blue eyes, detailed skin texture, professional lighting",
        "A majestic mountain landscape with a lake, sunset, detailed, high resolution",
        "Digital art of a futuristic city with neon lights and flying cars",
        "A fantasy character, detailed armor, magic effects, dramatic lighting, high detail"
    ]
