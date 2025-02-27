import gradio as gr
import argparse
import os
import logging
from txt2img import generate_image_from_text
from img2img import generate_image_from_image
from img2vid import generate_video_from_images
from workflow import run_workflow
from utils import check_system_info, display_server_info
from model_manager import (
    list_available_models, 
    list_available_loras, 
    get_prompt_suggestions,
    download_all_models
)

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
    parser.add_argument("--download-models", action="store_true", help="Tüm modelleri indir")
    args = parser.parse_args()
    
    # Debug modu
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug modu etkinleştirildi")
    
    # Tüm modelleri indir
    if args.download_models:
        logger.info("Tüm modeller indiriliyor...")
        download_all_models()
        logger.info("Model indirme tamamlandı")
    
    # Sistem bilgisini kontrol et ve göster
    system_info = check_system_info()
    
    # Kullanılabilir modelleri ve LoRA'ları al
    models = list_available_models()
    loras = list_available_loras()
    
    # Model seçeneklerini oluştur
    model_choices = [(model_info["name"], model_id) for model_id, model_info in models.items()]
    
    # LoRA seçeneklerini oluştur
    lora_choices = [("Yok", None)] + [(lora_info["name"], lora_id) for lora_id, lora_info in loras.items()]
    
    with gr.Blocks(title="AI Görsel Oluşturma") as app:
        gr.Markdown("# 🎨 AI Görsel Oluşturma Aracı")
        
        # Sistem bilgisini görsel olarak göster
        if system_info["gpu_available"]:
            gr.Markdown(f"### ✅ **GPU Aktif**: {system_info['device_name']}")
            if "gpu_memory_total" in system_info:
                gr.Markdown(f"GPU Bellek: {system_info.get('gpu_memory_used', '?')} / {system_info['gpu_memory_total']}")
        else:
            gr.Markdown("### ⚠️ **GPU Bulunmadı**: Performans düşük olabilir")
            gr.Markdown("> ℹ️ **Bilgi**: Sistem CPU kullanıyor. İşlemler yavaş olabilir.")
        
        # Düşük bellek modu uyarısı
        if args.low_memory:
            gr.Markdown("### 🔄 Düşük Bellek Modu Aktif: Daha yavaş işlem, daha az bellek kullanımı")
        
        with gr.Tab("Metin → Görsel"):
            with gr.Row():
                with gr.Column():
                    # Model seçimi
                    model_dropdown = gr.Dropdown(
                        choices=model_choices, 
                        value=model_choices[0][1], 
                        label="Model Seçimi"
                    )
                    
                    # LoRA seçimi
                    lora_dropdown = gr.Dropdown(
                        choices=lora_choices, 
                        value=lora_choices[0][1],
                        label="LoRA Adaptasyonu (opsiyonel)"
                    )
                    
                    text_input = gr.Textbox(
                        label="Görsel açıklaması", 
                        lines=3, 
                        placeholder="Detaylı bir görsel açıklaması girin..."
                    )
                    
                    # Prompt önerileri
                    example_prompts = gr.Examples(
                        examples=[
                            "A photorealistic portrait of a young woman with blue eyes, detailed skin texture, professional lighting",
                            "A majestic mountain landscape with a lake, sunset, detailed, high resolution",
                            "Digital art of a futuristic city with neon lights and flying cars",
                            "A fantasy character, detailed armor, magic effects, dramatic lighting, high detail"
                        ],
                        inputs=text_input,
                        label="Öneri Promptlar"
                    )
                    
                    prompt_guidance = gr.Slider(
                        label="Prompt Yönlendirme Gücü", 
                        minimum=1, 
                        maximum=20, 
                        value=7.5, 
                        step=0.5
                    )
                    
                    num_steps = gr.Slider(
                        label="Diffusion Adımları", 
                        minimum=10, 
                        maximum=100, 
                        value=50 if not args.low_memory else 30, 
                        step=1
                    )
                    
                    generate_btn = gr.Button("Görsel Oluştur", variant="primary")
                    
                with gr.Column():
                    image_output = gr.Image(label="Oluşturulan Görsel")
                    output_status = gr.Markdown("*Görsel oluşturmak için sol taraftaki ayarları yapın ve 'Görsel Oluştur' butonuna tıklayın.*")
            
            # Prompt önerilerini model değişikliğinde güncelle
            def update_prompt_examples(model_id):
                suggestions = get_prompt_suggestions(model_id)
                return gr.Examples.update(examples=suggestions)
            
            # Bu satırı kaldırın veya yorum satırı yapın:
            # model_dropdown.change(
            #     fn=update_prompt_examples,
            #     inputs=[model_dropdown],
            #     outputs=[example_prompts]
            # )
            
            # Alternatif olarak, örnek açıklamalarını statik olarak belirleyin:
            example_prompts = gr.Examples(
                examples=[
                    "A photorealistic portrait of a young woman with blue eyes, detailed skin texture, professional lighting",
                    "A majestic mountain landscape with a lake, sunset, detailed, high resolution",
                    "Digital art of a futuristic city with neon lights and flying cars",
                    "A fantasy character, detailed armor, magic effects, dramatic lighting, high detail"
                ],
                inputs=text_input,
                label="Öneri Promptlar"
            )

            # txt2img işlemi için fonksiyon
            def generate_wrapper(prompt, guidance, steps, model_id, lora_id):
                output_status_value = "Görsel oluşturuluyor... Lütfen bekleyin."
                try:
                    # Kullanıcıya işlem başladığını haber ver
                    logger.info(f"'{prompt}' için görsel oluşturuluyor (Model: {model_id}, LoRA: {lora_id if lora_id else 'Yok'})")
                    
                    # Görseli oluştur
                    image = generate_image_from_text(
                        prompt=prompt, 
                        guidance_scale=guidance, 
                        num_steps=steps,
                        model_id=model_id,
                        lora_id=lora_id,
                        low_memory=args.low_memory,
                        debug=args.debug
                    )
                    
                    if image:
                        output_status_value = "Görsel başarıyla oluşturuldu!"
                        logger.info("Görsel başarıyla oluşturuldu")
                    else:
                        output_status_value = "Görsel oluşturulamadı!"
                        logger.error("Görsel oluşturma başarısız")
                    
                    return image, output_status_value
                except Exception as e:
                    logger.error(f"Görsel oluşturma hatası: {e}")
                    output_status_value = f"Hata: {str(e)}"
                    return None, output_status_value
            
            # Görsel oluşturma butonunun tıklanma olayı
            generate_btn.click(
                fn=generate_wrapper,
                inputs=[text_input, prompt_guidance, num_steps, model_dropdown, lora_dropdown],
                outputs=[image_output, output_status]
            )
        
        with gr.Tab("Görsel → Görsel"):
            with gr.Row():
                with gr.Column():
                    # Model seçimi
                    img2img_model_dropdown = gr.Dropdown(
                        choices=model_choices, 
                        value=model_choices[0][1], 
                        label="Model Seçimi"
                    )
                    
                    source_image = gr.Image(label="Kaynak Görsel", type="pil")
                    img2img_prompt = gr.Textbox(label="İstediğiniz değişiklik", lines=2)
                    strength = gr.Slider(label="Değişim Miktarı", minimum=0.1, maximum=1.0, value=0.8, step=0.05)
                    img2img_steps = gr.Slider(label="Diffusion Adımları", minimum=10, maximum=100, value=30, step=1)
                    img2img_btn = gr.Button("Dönüştür")
                with gr.Column():
                    img2img_output = gr.Image(label="Dönüştürülmüş Görsel")
                    img2img_status = gr.Markdown("*Görseli dönüştürmek için önce kaynak görsel seçin ve istediğiniz değişikliği yazın.*")
            
            # img2img işlemi için fonksiyon
            def img2img_wrapper(init_image, prompt, strength, steps, model_id):
                if init_image is None:
                    return None, "Lütfen bir kaynak görsel seçin!"
                
                status_value = "Görsel dönüştürülüyor... Lütfen bekleyin."
                try:
                    # Görseli dönüştür
                    image = generate_image_from_image(
                        init_image=init_image,
                        prompt=prompt,
                        strength=strength,
                        num_steps=steps,
                        model_id=model_id,
                        low_memory=args.low_memory
                    )
                    
                    if image:
                        status_value = "Görsel başarıyla dönüştürüldü!"
                    else:
                        status_value = "Görsel dönüştürülemedi!"
                    
                    return image, status_value
                except Exception as e:
                    logger.error(f"Görsel dönüştürme hatası: {e}")
                    return None, f"Hata: {str(e)}"
            
            img2img_btn.click(
                fn=img2img_wrapper,
                inputs=[source_image, img2img_prompt, strength, img2img_steps, img2img_model_dropdown],
                outputs=[img2img_output, img2img_status]
            )
        
        with gr.Tab("Görsel → Video"):
            with gr.Row():
                with gr.Column():
                    video_source_image = gr.Image(label="Başlangıç Görseli", type="pil")
                    video_frames = gr.Slider(label="Video Kare Sayısı", minimum=10, maximum=120, value=30, step=10)
                    video_fps = gr.Slider(label="FPS", minimum=5, maximum=30, value=15, step=5)
                    motion_scale = gr.Slider(label="Hareket Ölçeği", minimum=1, maximum=50, value=25, step=1)
                    img2vid_btn = gr.Button("Video Oluştur")
                    img2vid_status = gr.Markdown("*Video oluşturmak için bir başlangıç görseli seçin.*")
                with gr.Column():
                    video_output = gr.Video(label="Oluşturulan Video")
            
            # img2vid işlemi için fonksiyon
            def img2vid_wrapper(image, frames, fps, motion):
                if image is None:
                    return None, "Lütfen bir başlangıç görseli seçin!"
                
                try:
                    video_path = generate_video_from_images(
                        source_image=image, 
                        num_frames=frames, 
                        fps=fps, 
                        motion_scale=motion
                    )
                    
                    if video_path:
                        return video_path, "Video başarıyla oluşturuldu!"
                    else:
                        return None, "Video oluşturulamadı!"
                except Exception as e:
                    logger.error(f"Video oluşturma hatası: {e}")
                    return None, f"Hata: {str(e)}"
            
            img2vid_btn.click(
                fn=img2vid_wrapper,
                inputs=[video_source_image, video_frames, video_fps, motion_scale],
                outputs=[video_output, img2vid_status]
            )
            
        with gr.Tab("İş Akışı"):
            with gr.Row():
                with gr.Column():
                    workflow_prompt = gr.Textbox(label="Metin Açıklaması", lines=3)
                    workflow_type = gr.Dropdown(
                        label="İş Akışı Tipi", 
                        choices=["Basit", "Stil Transferi", "Gelişmiş Düzenleme"], 
                        value="Basit"
                    )
                    workflow_btn = gr.Button("İş Akışını Çalıştır")
                    workflow_status = gr.Markdown("*İş akışını başlatmak için bir metin açıklaması girin ve akış tipini seçin.*")
                with gr.Column():
                    workflow_output = gr.Gallery(label="İş Akışı Sonuçları")
            
            # İş akışı için fonksiyon
            def workflow_wrapper(prompt, workflow_type):
                if not prompt:
                    return [], "Lütfen bir metin açıklaması girin!"
                
                try:
                    workflow_status_value = f"{workflow_type} iş akışı başlatılıyor... Lütfen bekleyin."
                    images = run_workflow(prompt, workflow_type)
                    
                    if images and len(images) > 0:
                        workflow_status_value = f"{len(images)} görsel başarıyla oluşturuldu!"
                        return images, workflow_status_value
                    else:
                        workflow_status_value = "İş akışı başarısız oldu veya hiç görsel oluşturulamadı!"
                        return [], workflow_status_value
                except Exception as e:
                    logger.error(f"İş akışı hatası: {e}")
                    return [], f"Hata: {str(e)}"
            
            workflow_btn.click(
                fn=workflow_wrapper,
                inputs=[workflow_prompt, workflow_type],
                outputs=[workflow_output, workflow_status]
            )
        
        # Model ve LoRA bilgileri sekmesi
        with gr.Tab("Bilgi ve Modeller"):
            gr.Markdown("## 📚 Kullanılan Modeller ve LoRA Adaptasyonları")
            
            gr.Markdown("### 🔮 Modeller")
            model_info_md = ""
            for model_id, model_info in models.items():
                model_info_md += f"- **{model_info['name']}** ({model_id}): {model_info['description']}\n"
            gr.Markdown(model_info_md)
            
            gr.Markdown("### 🎭 LoRA Adaptasyonları")
            lora_info_md = ""
            for lora_id, lora_info in loras.items():
                lora_info_md += f"- **{lora_info['name']}** ({lora_id}): {lora_info['description']}\n"
            gr.Markdown(lora_info_md)
            
            gr.Markdown("## 🖥️ Sistem Bilgisi")
            sys_info_md = f"""
            - **İşletim Sistemi**: {system_info['system']}
            - **Python Sürümü**: {system_info['python_version']}
            - **GPU**: {'✅ ' + system_info['device_name'] if system_info['gpu_available'] else '❌ Yok'}
            - **RAM**: {system_info['memory_gb']} GB
            """
            gr.Markdown(sys_info_md)
            
            gr.Markdown("""
            ## 📝 Kullanım İpuçları
            
            - Daha iyi sonuçlar için detaylı promptlar kullanın
            - "Pony Realism" modeli gerçekçi görseller için çok başarılıdır
            - Düşük bellek modunda sorun yaşıyorsanız, diffusion adımlarını azaltın
            - Metin açıklamasında istediğiniz detayları belirtin (örn: "aydınlık", "detaylı", "profesyonel fotoğraf")
            """)
    
    # Geliştirici modu
    if args.debug:
        print(f"Debug modu aktif: {args.debug}")
        print(f"Modeller: {list(models.keys())}")
        print(f"LoRA'lar: {list(loras.keys())}")
    
    # Uygulamayı başlat
    app.launch(
        server_name="0.0.0.0", 
        server_port=args.port, 
        share=args.share,
        debug=args.debug
    )

if __name__ == "__main__":
    main()
