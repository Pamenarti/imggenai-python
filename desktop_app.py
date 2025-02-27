import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, StringVar
import threading
import torch
import psutil
import webbrowser
from PIL import Image, ImageTk

# Modülleri yükle
from txt2img import generate_image_from_text
from img2img import generate_image_from_image
from utils import check_system_info

class AIImageGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Görsel Oluşturma")
        self.root.geometry("1000x700")
        
        # GPU kullanım limiti (varsayılan %20)
        self.gpu_limit = 20
        
        # Ana çerçeveleri oluştur
        self.setup_ui()
        
        # GPU bilgisini kontrol et
        self.check_gpu()
        
        # Web sunucusunu başlat (arka planda)
        self.start_web_server()
        
    def setup_ui(self):
        # Ana sekme düzeni
        self.tab_control = ttk.Notebook(self.root)
        
        # Sekmeler
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab4 = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab1, text="Metin → Görsel")
        self.tab_control.add(self.tab2, text="Görsel → Görsel")
        self.tab_control.add(self.tab3, text="Ayarlar")
        self.tab_control.add(self.tab4, text="Bilgi")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Metin → Görsel sekmesi
        self.setup_text2img_tab()
        
        # Görsel → Görsel sekmesi
        self.setup_img2img_tab()
        
        # Ayarlar sekmesi
        self.setup_settings_tab()
        
        # Bilgi sekmesi
        self.setup_info_tab()
        
    def setup_text2img_tab(self):
        # Prompt alanı
        ttk.Label(self.tab1, text="Görsel açıklaması:").grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.txt_prompt = tk.Text(self.tab1, height=4, width=50)
        self.txt_prompt.grid(column=0, row=1, padx=10, pady=5, sticky="nsew")
        
        # Ayarlar çerçevesi
        settings_frame = ttk.LabelFrame(self.tab1, text="Ayarlar")
        settings_frame.grid(column=0, row=2, padx=10, pady=10, sticky="nsew")
        
        # Guidance scale
        ttk.Label(settings_frame, text="Prompt Yönlendirme Gücü:").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.slider_guidance = ttk.Scale(settings_frame, from_=1, to=20, value=7.5, orient="horizontal")
        self.slider_guidance.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.lbl_guidance = ttk.Label(settings_frame, text="7.5")
        self.lbl_guidance.grid(column=2, row=0, padx=5, pady=5)
        self.slider_guidance.configure(command=lambda v: self.lbl_guidance.configure(text=f"{float(v):.1f}"))
        
        # Diffusion adımları
        ttk.Label(settings_frame, text="Diffusion Adımları:").grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.slider_steps = ttk.Scale(settings_frame, from_=10, to=100, value=50, orient="horizontal")
        self.slider_steps.grid(column=1, row=1, padx=5, pady=5, sticky="ew")
        self.lbl_steps = ttk.Label(settings_frame, text="50")
        self.lbl_steps.grid(column=2, row=1, padx=5, pady=5)
        self.slider_steps.configure(command=lambda v: self.lbl_steps.configure(text=f"{int(float(v))}"))
        
        # GPU kullanım limiti
        ttk.Label(settings_frame, text="GPU Kullanım Limiti (%):").grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.slider_gpu = ttk.Scale(settings_frame, from_=5, to=100, value=self.gpu_limit, orient="horizontal")
        self.slider_gpu.grid(column=1, row=2, padx=5, pady=5, sticky="ew")
        self.lbl_gpu = ttk.Label(settings_frame, text=f"{self.gpu_limit}")
        self.lbl_gpu.grid(column=2, row=2, padx=5, pady=5)
        self.slider_gpu.configure(command=lambda v: self.update_gpu_limit(v))
        
        # Butonlar
        btn_frame = ttk.Frame(self.tab1)
        btn_frame.grid(column=0, row=3, padx=10, pady=10, sticky="w")
        
        ttk.Button(btn_frame, text="Görsel Oluştur", command=self.generate_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Kaydet", command=self.save_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Temizle", command=self.clear_image).pack(side="left", padx=5)
        
        # Görsel görüntüleme alanı
        self.img_label = ttk.Label(self.tab1)
        self.img_label.grid(column=1, row=0, rowspan=4, padx=10, pady=10, sticky="nsew")
        
        # Durum çubuğu
        self.status_var = StringVar()
        self.status_var.set("Hazır")
        self.status_bar = ttk.Label(self.tab1, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.grid(column=0, row=4, columnspan=2, padx=0, sticky="sew")
        
        # Sütun ve satır ağırlıkları
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.columnconfigure(1, weight=3)
        self.tab1.rowconfigure(4, weight=1)
        
    def setup_img2img_tab(self):
        # Bu sekme için temel UI elemanları
        ttk.Label(self.tab2, text="Önce bir görsel seçin, sonra dönüştürme istediğinizi belirtin").grid(column=0, row=0, padx=10, pady=10)
        ttk.Button(self.tab2, text="Görsel Seç", command=self.select_image).grid(column=0, row=1, padx=10, pady=10)
        
    def setup_settings_tab(self):
        # GPU kullanım ayarları
        gpu_frame = ttk.LabelFrame(self.tab3, text="GPU Ayarları")
        gpu_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(gpu_frame, text="Maksimum GPU Kullanımı (%)").grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.gpu_limit_slider = ttk.Scale(gpu_frame, from_=5, to=100, value=self.gpu_limit, orient="horizontal")
        self.gpu_limit_slider.grid(column=1, row=0, padx=10, pady=10, sticky="ew")
        self.gpu_limit_label = ttk.Label(gpu_frame, text=f"{self.gpu_limit}%")
        self.gpu_limit_label.grid(column=2, row=0, padx=10, pady=10)
        self.gpu_limit_slider.configure(command=lambda v: self.update_gpu_limit(v))
        
        # Web arayüzü ayarları
        web_frame = ttk.LabelFrame(self.tab3, text="Web Arayüzü")
        web_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(web_frame, text="Web arayüzünü tarayıcıda aç").grid(column=0, row=0, padx=10, pady=10, sticky="w")
        ttk.Button(web_frame, text="Tarayıcıda Aç", command=self.open_browser).grid(column=1, row=0, padx=10, pady=10)
        
        # Model ayarları
        model_frame = ttk.LabelFrame(self.tab3, text="Model Ayarları")
        model_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(model_frame, text="Model:").grid(column=0, row=0, padx=10, pady=10, sticky="w")
        models = ["stable-diffusion-v1-5", "stable-diffusion-2-1", "dreamlike-diffusion-1.0"]
        self.model_var = StringVar()
        self.model_var.set(models[0])
        ttk.Combobox(model_frame, textvariable=self.model_var, values=models).grid(column=1, row=0, padx=10, pady=10, sticky="ew")
        
    def setup_info_tab(self):
        # Sistem bilgisi
        sys_frame = ttk.LabelFrame(self.tab4, text="Sistem Bilgisi")
        sys_frame.pack(fill="x", padx=10, pady=10)
        
        self.sys_info_text = tk.Text(sys_frame, height=10, width=60, wrap="word")
        self.sys_info_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.sys_info_text.config(state="normal")
        self.sys_info_text.delete(1.0, tk.END)
        
        # Bilgileri doldur
        system_info = check_system_info()
        info_text = f"""
        İşletim Sistemi: {system_info['system']}
        Python Sürümü: {system_info['python_version']}
        Torch Sürümü: {system_info['torch_version']}
        CPU Çekirdek Sayısı: {system_info['cpu_count']}
        RAM: {system_info['memory_gb']} GB
        
        GPU Bilgisi:
        - GPU Mevcut: {'Evet' if system_info['gpu_available'] else 'Hayır'}
        - GPU Adı: {system_info['device_name']}
        - GPU Sayısı: {system_info['device_count']}
        
        Kullanıcı GPU Limiti: %{self.gpu_limit}
        """
        self.sys_info_text.insert(tk.END, info_text)
        self.sys_info_text.config(state="disabled")
        
        # Yapım ve lisans bilgileri
        about_frame = ttk.LabelFrame(self.tab4, text="Hakkında")
        about_frame.pack(fill="x", padx=10, pady=10)
        
        about_text = """
        AI Görsel Oluşturma v1.0
        
        Bu uygulama, kullanıcıların kendi GPU'larını kullanarak 
        yapay zeka ile görsel oluşturmasına olanak tanır.
        
        © 2023 AI Görsel Oluşturma Ekibi
        """
        
        ttk.Label(about_frame, text=about_text, wraplength=500).pack(padx=10, pady=10)
        
    def check_gpu(self):
        # GPU varlığını kontrol et
        self.has_gpu = torch.cuda.is_available()
        
        if self.has_gpu:
            # GPU bellek bilgisini al
            self.gpu_name = torch.cuda.get_device_name(0)
            if hasattr(torch.cuda, "get_device_properties"):
                prop = torch.cuda.get_device_properties(0)
                self.gpu_memory = prop.total_memory / (1024**3)  # GB cinsinden
                
                # Bilgiyi güncelle
                status_text = f"GPU: {self.gpu_name} ({self.gpu_memory:.2f} GB) - Limit: %{self.gpu_limit}"
                self.status_var.set(status_text)
                
                # GPU kullanım limitini ayarla
                self.set_gpu_memory_limit(self.gpu_limit)
        else:
            self.status_var.set("GPU bulunamadı! CPU kullanılacak.")
            
    def set_gpu_memory_limit(self, percentage):
        """GPU bellek kullanımını yüzde olarak sınırla"""
        if not self.has_gpu:
            return
            
        try:
            # Toplam GPU belleği
            total_memory = torch.cuda.get_device_properties(0).total_memory
            # Yüzdeyi hesapla
            max_memory = int(total_memory * (percentage / 100))
            
            # PyTorch için bellek sınırını ayarla
            torch.cuda.set_per_process_memory_fraction(percentage / 100)
            
            print(f"GPU bellek limiti %{percentage} olarak ayarlandı ({max_memory/(1024**3):.2f} GB)")
        except Exception as e:
            print(f"GPU bellek limiti ayarlanamadı: {e}")
    
    def update_gpu_limit(self, value):
        """GPU kullanım limitini güncelle"""
        limit = int(float(value))
        self.gpu_limit = limit
        self.lbl_gpu.configure(text=f"{limit}")
        self.gpu_limit_label.configure(text=f"{limit}%")
        
        # GPU bellek limitini ayarla
        self.set_gpu_memory_limit(limit)
    
    def generate_image(self):
        """Metin açıklamasından görsel oluştur"""
        prompt = self.txt_prompt.get("1.0", "end-1c")
        guidance_scale = float(self.slider_guidance.get())
        steps = int(float(self.slider_steps.get()))
        
        if not prompt:
            self.status_var.set("Lütfen bir görsel açıklaması girin!")
            return
            
        self.status_var.set("Görsel oluşturuluyor...")
        self.root.update()
        
        # Thread'de işlem yap
        def process():
            try:
                # GPU limitini ayarla
                self.set_gpu_memory_limit(self.gpu_limit)
                
                # Görseli oluştur
                img = generate_image_from_text(prompt, guidance_scale, steps)
                
                # Görüntüle
                self.display_image(img)
                self.status_var.set(f"Görsel oluşturuldu: {prompt[:30]}...")
            except Exception as e:
                self.status_var.set(f"Hata: {str(e)}")
                
        threading.Thread(target=process).start()
    
    def display_image(self, img):
        """Oluşturulan görseli göster"""
        if not img:
            return
            
        # Resmi kaydet ve göster
        self.result_image = img
        
        # Tkinter için uygun formata dönüştür
        img = img.resize((512, 512))
        photo = ImageTk.PhotoImage(img)
        
        # Görsel etiketini güncelle
        self.img_label.configure(image=photo)
        self.img_label.image = photo
    
    def save_image(self):
        """Oluşturulan görseli kaydet"""
        if not hasattr(self, "result_image"):
            self.status_var.set("Kaydedilecek görsel yok!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            self.result_image.save(file_path)
            self.status_var.set(f"Görsel kaydedildi: {file_path}")
    
    def clear_image(self):
        """Görseli temizle"""
        if hasattr(self, "result_image"):
            del self.result_image
            
        self.img_label.configure(image="")
        self.txt_prompt.delete("1.0", tk.END)
        self.status_var.set("Hazır")
    
    def select_image(self):
        """Görsel seç (img2img için)"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        
        if file_path:
            self.status_var.set(f"Görsel seçildi: {file_path}")
            # Burada img2img işlevselliği eklenebilir
    
    def start_web_server(self):
        """Arka planda web sunucusu başlat"""
        def run_server():
            import subprocess
            
            # Geçerli çalışma dizinini al
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Web sunucusunu başlat (port çakışmaları için farklı port)
            cmd = [sys.executable, os.path.join(current_dir, "web_server.py"), "--port", "7860", "--gpu-limit", str(self.gpu_limit)]
            subprocess.Popen(cmd)
            
        threading.Thread(target=run_server, daemon=True).start()
    
    def open_browser(self):
        """Web arayüzünü tarayıcıda aç"""
        webbrowser.open("http://localhost:7860")

# Uygulamayı başlat
def main():
    root = tk.Tk()
    app = AIImageGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
