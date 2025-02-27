import gradio as gr
import argparse
import os
import logging
from txt2img import generate_image_from_text
from img2img import generate_image_from_image
from img2vid import generate_video_from_images
from workflow import run_workflow
from utils import check_system_info

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Komut satırı argümanlarını işle
    parser = argparse.ArgumentParser(description="AI Görsel Oluşturma")
    parser.add_argument("--share", action="store_true", help="Arayüzü internet üzerinden paylaş")
    parser.add_argument("--port", type=int, default=7860, help="Web sunucusu port numarası")
    parser.add_argument("--debug", action="store_true", help="Hata ayıklama modunu etkinleştir")
    parser.add_argument("--low-memory", action="store_true", help="Düşük bellek modu")
    args = parser.parse_args()
    
    # Debug modu
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug modu aktif")
    
    # Sistem bilgisini kontrol et ve göster
    system_info = check_system_info()
    
    with gr.Blocks(title="AI Görsel Oluşturma") as app:
        gr.Markdown("# 🎨 AI Görsel Oluşturma Aracı")
        
        # Sistem bilgisini görsel olarak göster
        if system_info["gpu_available"]:
            gr.Markdown(f"### ✅ **GPU Aktif**: {system_info['device_name']}")
            gr.Markdown("> ℹ️ **Bilgi**: Hesaplamalar bu uygulamanın çalıştığı bilgisayardaki GPU ile yapılmaktadır.")
        else:
            gr.Markdown("### ⚠️ **GPU Bulunmadı**: Performans düşük olabilir")
            gr.Markdown("> ℹ️ **Bilgi**: Sistem CPU kullanıyor. İşlemler yavaş olabilir.")
        
        # Düşük bellek modu uyarısı
        if args.low_memory:
            gr.Markdown("### 🔄 Düşük Bellek Modu Aktif: Daha yavaş işlem, daha az bellek kullanımı")
        
        # Ana sekmeleri oluştur
        with gr.Tab("Metin → Görsel"):
            # ...existing code...
            
        with gr.Tab("Görsel → Görsel"):
            # ...existing code...
        
        with gr.Tab("Görsel → Video"):
            # ...existing code...
            
        with gr.Tab("İş Akışı"):
            # ...existing code...
    
    # Uygulamayı başlat - En basit API kullanımı
    try:
        logger.info(f"Uygulama başlatılıyor: port={args.port}, share={args.share}")
        # Queue kullanmadan direkt launch et
        app.launch(
            server_name="0.0.0.0",  # Tüm ağ arayüzlerine bağlan
            share=args.share, 
            server_port=args.port
        )
    except Exception as e:
        logger.error(f"Başlatma hatası: {e}")
        logger.info("Yerel modda devam ediliyor...")
        app.launch(
            server_name="127.0.0.1",  # Sadece yerel bağlantılar
            share=False, 
            server_port=args.port
        )

if __name__ == "__main__":
    main()
