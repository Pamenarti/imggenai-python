import torch
import numpy as np
import os
import tempfile
import cv2
import logging
from PIL import Image, ImageDraw, ImageFont
import shutil
from pathlib import Path
import time
import subprocess

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

def generate_video_from_images(
    source_image, 
    num_frames=30, 
    fps=15, 
    motion_scale=10.0,
    output_dir="/home/agrotest2/imggenai/outputs"
):
    """
    Tek bir görselden basit hareket efektleri ekleyerek video oluşturur.
    
    Args:
        source_image: PIL.Image - Kaynak görsel
        num_frames: int - Video kareleri sayısı
        fps: int - Video FPS değeri
        motion_scale: float - Hareket şiddeti
        output_dir: str - Çıktı dizini
    
    Returns:
        str: Oluşturulan video dosyasının yolu veya None (başarısız olursa)
    """
    try:
        start_time = time.time()
        logger.info(f"Video oluşturuluyor: {num_frames} kare, {fps} FPS")
        
        # Çıktı dizinini kontrol et
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Basit bir hareket/zoom/pan efekti oluştur
        frames = []
        output_size = source_image.size
        
        # MoviePy kurulu değilse bunu çalıştır - basit animasyon
        if not MOVIEPY_AVAILABLE:
            return generate_basic_video(source_image, num_frames, fps, motion_scale, output_path)
            
        # MoviePy kullanarak video oluştur
        for i in range(num_frames):
            # Zaman bazlı değişken değerler (sin/cos fonksiyonları ile)
            time_val = i / num_frames
            
            # Basit zoom ve pan efekti
            zoom = 1.0 + 0.1 * np.sin(time_val * 2 * np.pi) * (motion_scale / 10)
            pan_x = 0.05 * np.sin(time_val * 3 * np.pi) * motion_scale
            pan_y = 0.05 * np.cos(time_val * 2 * np.pi) * motion_scale
            
            # Yeni kare oluştur - basit transformasyon
            frame = source_image.copy()
            new_size = (int(frame.width * zoom), int(frame.height * zoom))
            frame = frame.resize(new_size, Image.LANCZOS)
            
            # Pan efekti için kaydırma
            x_offset = int(pan_x * frame.width)
            y_offset = int(pan_y * frame.height)
            
            # Ortalama görünüm oluştur
            x_crop = (frame.width - output_size[0]) // 2 + x_offset
            y_crop = (frame.height - output_size[1]) // 2 + y_offset
            
            # Kesme sınırlarını kontrol et
            x_crop = max(0, min(x_crop, frame.width - output_size[0]))
            y_crop = max(0, min(y_crop, frame.height - output_size[1]))
            
            # Görüntüyü kırp ve listeye ekle
            cropped = frame.crop((x_crop, y_crop, x_crop + output_size[0], y_crop + output_size[1]))
            frames.append(np.array(cropped))
        
        # Video dosyasını oluştur
        output_file = output_path / f"video_{int(time.time())}.mp4"
        clip = ImageSequenceClip(frames, fps=fps)
        clip.write_videofile(str(output_file), codec="libx264", audio=False)
        
        elapsed = time.time() - start_time
        logger.info(f"Video oluşturma tamamlandı: {output_file} ({elapsed:.2f} saniye)")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Video oluşturulurken hata: {e}", exc_info=True)
        return None

def generate_basic_video(source_image, num_frames, fps, motion_scale, output_path):
    """
    MoviePy olmadığında basit bir video oluşturmak için alternatif fonksiyon.
    FFmpeg kullanılarak basit bir animasyon yapılır.
    """
    try:
        # Geçici klasör oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            # Basit animasyon için görselleri oluştur
            output_size = source_image.size
            
            for i in range(num_frames):
                # Zaman bazlı değişken değerler (sin/cos fonksiyonları ile)
                time_val = i / num_frames
                
                # Basit zoom ve pan efekti
                zoom = 1.0 + 0.1 * np.sin(time_val * 2 * np.pi) * (motion_scale / 10)
                pan_x = 0.05 * np.sin(time_val * 3 * np.pi) * motion_scale
                pan_y = 0.05 * np.cos(time_val * 2 * np.pi) * motion_scale
                
                # Yeni kare oluştur - basit transformasyon
                frame = source_image.copy()
                new_size = (int(frame.width * zoom), int(frame.height * zoom))
                frame = frame.resize(new_size, Image.LANCZOS)
                
                # Pan efekti için kaydırma
                x_offset = int(pan_x * frame.width)
                y_offset = int(pan_y * frame.height)
                
                # Ortalama görünüm oluştur
                x_crop = (frame.width - output_size[0]) // 2 + x_offset
                y_crop = (frame.height - output_size[1]) // 2 + y_offset
                
                # Kesme sınırlarını kontrol et
                x_crop = max(0, min(x_crop, frame.width - output_size[0]))
                y_crop = max(0, min(y_crop, frame.height - output_size[1]))
                
                # Görüntüyü kırp ve kaydet
                cropped = frame.crop((x_crop, y_crop, x_crop + output_size[0], y_crop + output_size[1]))
                frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                cropped.save(frame_path)
            
            # FFmpeg ile video oluştur
            output_file = output_path / f"video_{int(time.time())}.mp4"
            
            try:
                # FFmpeg komutunu oluştur
                ffmpeg_cmd = [
                    "ffmpeg", 
                    "-y",  # Var olan dosyanın üzerine yaz
                    "-framerate", str(fps),  # FPS ayarı
                    "-i", os.path.join(temp_dir, "frame_%04d.png"),  # Giriş dosyaları
                    "-c:v", "libx264",  # Video codec
                    "-pix_fmt", "yuv420p",  # Pixel formatı
                    "-crf", "23",  # Kalite (düşük değer daha iyi kalite)
                    str(output_file)
                ]
                
                # FFmpeg'i çalıştır
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                logger.info(f"FFmpeg ile video başarıyla oluşturuldu: {output_file}")
                return str(output_file)
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"FFmpeg ile video oluşturulurken hata: {e}")
                
                # Alternatif yöntem: Kare kare birleştirme
                first_frame = Image.open(os.path.join(temp_dir, "frame_0000.png"))
                animated_gif = output_path / f"animation_{int(time.time())}.gif"
                
                # Tüm kareleri topla
                frames_img = []
                for i in range(num_frames):
                    frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                    frames_img.append(Image.open(frame_path))
                
                # GIF olarak kaydet
                first_frame.save(
                    animated_gif,
                    save_all=True,
                    append_images=frames_img[1:],
                    duration=int(1000/fps),  # Milisaniye cinsinden
                    loop=0
                )
                logger.info(f"Basit GIF animasyonu oluşturuldu: {animated_gif}")
                return str(animated_gif)
    
    except Exception as e:
        logger.error(f"Basit video oluşturulurken hata: {e}", exc_info=True)
        return None

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
