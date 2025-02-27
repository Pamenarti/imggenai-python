import torch
import numpy as np
import os
import tempfile
import cv2
import logging
from PIL import Image, ImageDraw, ImageFont

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MoviePy modülünü kontrollü bir şekilde import et
try:
    from moviepy.editor import ImageSequenceClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    logger.warning("MoviePy kütüphanesi yüklü değil! Video oluşturma özelliği sınırlı olabilir.")
    logger.warning("Yüklemek için: pip install moviepy")
    MOVIEPY_AVAILABLE = False

def generate_video_from_images(source_image, num_frames=30, fps=15, motion_scale=25, effect_type="zoom_pan"):
    """
    Tek bir görselden hareketli video oluşturma
    
    Args:
        source_image: Kaynak görsel (PIL Image)
        num_frames: Video kare sayısı
        fps: Saniyedeki kare sayısı
        motion_scale: Hareket ölçeği (daha büyük değerler = daha fazla hareket)
        effect_type: Hareket efekti tipi ("zoom_pan", "rotate", "wave")
        
    Returns:
        Oluşturulan video dosyasının yolu
    """
    try:
        if source_image is None:
            logger.error("Video oluşturulamadı: Kaynak görsel yok")
            return None
            
        # MoviePy kontrolü
        if not MOVIEPY_AVAILABLE:
            logger.warning("MoviePy kütüphanesi yüklenmiş değil, basit video oluşturma yapılacak")
            video_path = create_simple_video(source_image, num_frames, fps, motion_scale)
            return video_path
                
        # Görüntü boyutları
        width, height = source_image.size
        target_size = (512, 512)  # Standart boyut
        
        # Görüntüyü yeniden boyutlandır
        source_image = source_image.resize(target_size)
        source_array = np.array(source_image)
        
        # Geçici dizin oluştur
        temp_dir = tempfile.mkdtemp()
        frames = []
        
        logger.info(f"Video oluşturuluyor: {num_frames} kare, {fps} FPS")
        
        # Efekt tipine göre video oluştur
        if effect_type == "rotate":
            frames = create_rotation_effect(source_array, num_frames, motion_scale)
        elif effect_type == "wave":
            frames = create_wave_effect(source_array, num_frames, motion_scale)
        else:  # Varsayılan: zoom_pan
            frames = create_zoom_pan_effect(source_array, num_frames, motion_scale)
        
        # Karelerden video oluştur
        video_path = os.path.join(temp_dir, "output_video.mp4")
        clip = ImageSequenceClip(frames, fps=fps)
        clip.write_videofile(video_path, codec='libx264', audio=False, preset='ultrafast')
        
        logger.info(f"Video başarıyla oluşturuldu: {video_path}")
        return video_path
        
    except Exception as e:
        logger.exception(f"Video oluşturma hatası: {e}")
        return None

def create_zoom_pan_effect(image, num_frames, scale):
    """Yakınlaştırma ve kaydırma efekti oluştur"""
    frames = []
    h, w = image.shape[:2]
    
    for i in range(num_frames):
        # Sinüs fonksiyonları ile organik hareketler oluştur
        progress = i / (num_frames - 1)  # 0'dan 1'e ilerleme
        
        # Yakınlaştırma faktörü (1.0 -> 1.2 -> 1.0)
        zoom = 1.0 + 0.2 * np.sin(progress * np.pi)
        
        # Kaydırma miktarı
        x_offset = int(scale * np.sin(progress * 2 * np.pi))
        y_offset = int(scale * np.cos(progress * 2 * np.pi))
        
        # Dönüşüm matrisi oluştur
        M = cv2.getRotationMatrix2D((w/2, h/2), 0, zoom)
        M[0, 2] += x_offset
        M[1, 2] += y_offset
        
        # Dönüşümü uygula
        frame = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        frames.append(frame)
    
    return frames

def create_rotation_effect(image, num_frames, scale):
    """Döndürme efekti oluştur"""
    frames = []
    h, w = image.shape[:2]
    
    for i in range(num_frames):
        progress = i / (num_frames - 1)  # 0'dan 1'e ilerleme
        
        # Döndürme açısı (-scale/2 -> scale/2 -> -scale/2)
        angle = scale * np.sin(progress * 2 * np.pi)
        
        # Yakınlaştırma faktörü (1.0 -> 1.1 -> 1.0)
        zoom = 1.0 + 0.1 * np.sin(progress * 2 * np.pi + np.pi/2)
        
        # Dönüşüm matrisi oluştur
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, zoom)
        
        # Dönüşümü uygula
        frame = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        frames.append(frame)
    
    return frames

def create_wave_effect(image, num_frames, scale):
    """Dalga efekti oluştur"""
    frames = []
    h, w = image.shape[:2]
    
    for i in range(num_frames):
        # Yeni frame oluştur
        frame = np.zeros_like(image)
        
        # Dalga parametreleri
        time = i / num_frames * 2 * np.pi
        wave_amplitude = scale / 10
        wave_frequency = 10
        
        # Her piksel için dalga efekti hesapla
        for y in range(h):
            offset_x = int(wave_amplitude * np.sin(wave_frequency * y / h + time))
            
            for x in range(w):
                src_x = (x - offset_x) % w
                frame[y, x] = image[y, src_x]
        
        frames.append(frame)
    
    return frames

def create_simple_video(image, num_frames, fps, scale):
    """MoviePy yoksa basit bir animasyonlu görsel oluştur"""
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "simple_animation.gif")
    
    # Görüntüyü yeniden boyutlandır
    image = image.resize((512, 512))
    
    # Kareler için liste
    frames = []
    
    # Basit bir zoom animasyonu oluştur
    for i in range(num_frames):
        # Geçiş faktörü
        t = i / (num_frames - 1)
        
        # Yakınlaştırma faktörü (1.0 -> 1.2 -> 1.0)
        zoom = 1.0 + 0.2 * np.sin(t * np.pi)
        
        # Yeni boyutları hesapla
        new_size = (int(image.width * zoom), int(image.height * zoom))
        
        # Görüntüyü yeniden boyutlandır
        resized = image.resize(new_size, Image.LANCZOS)
        
        # Kırpma koordinatları
        left = (resized.width - image.width) // 2
        top = (resized.height - image.height) // 2
        right = left + image.width
        bottom = top + image.height
        
        # Görüntüyü kırp
        cropped = resized.crop((left, top, right, bottom))
        frames.append(cropped)
    
    # Animasyon olarak kaydet
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),  # ms cinsinden
        loop=0  # Sonsuz döngü
    )
    
    return output_path

# Test için doğrudan çalıştırma
if __name__ == "__main__":
    # Test görseli
    test_image = Image.new('RGB', (512, 512), color='blue')
    draw = ImageDraw.Draw(test_image)
    draw.ellipse((100, 100, 400, 400), fill='red')
    draw.text((200, 250), "Test", fill='white')
    
    # Video oluştur
    video_path = generate_video_from_images(test_image)
    print(f"Test videosu oluşturuldu: {video_path}")
