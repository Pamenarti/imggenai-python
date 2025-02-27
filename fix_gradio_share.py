#!/usr/bin/env python3
"""
Bu script, Gradio paylaşım özelliği için gereken frpc dosyasını indirir ve yükler
"""

import os
import sys
import shutil
import platform
import requests
from pathlib import Path
import subprocess

def get_gradio_path():
    """Gradio kütüphanesinin kurulu olduğu dizini bulur"""
    try:
        import gradio
        return os.path.dirname(gradio.__file__)
    except ImportError:
        print("❌ Gradio kütüphanesi bulunamadı! Önce pip install gradio ile yükleyin.")
        return None

def get_frpc_url():
    """İşletim sistemine göre uygun frpc dosyasının URL'sini döndürür"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "linux":
        if arch in ["x86_64", "amd64"]:
            return "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64"
        elif "arm" in arch or "aarch64" in arch:
            return "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_arm64"
    elif system == "darwin":  # macOS
        if arch in ["x86_64", "amd64"]:
            return "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_darwin_amd64"
        elif "arm" in arch or "aarch64" in arch:
            return "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_darwin_arm64"
    elif system == "windows":
        return "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_windows_amd64.exe"
    
    return None

def download_frpc():
    """frpc dosyasını indirir ve Gradio klasörüne yerleştirir"""
    gradio_path = get_gradio_path()
    if not gradio_path:
        return False
    
    url = get_frpc_url()
    if not url:
        print("❌ Bu sistem için uygun frpc dosyası bulunamadı!")
        return False
    
    # İşletim sistemine göre dosya adını belirle
    system = platform.system().lower()
    version = "v0.3"
    
    if system == "windows":
        filename = f"frpc_windows_amd64_{version}.exe"
    elif system == "darwin":  # macOS
        arch = platform.machine().lower()
        arch_name = "arm64" if "arm" in arch or "aarch64" in arch else "amd64"
        filename = f"frpc_darwin_{arch_name}_{version}"
    else:  # linux
        arch = platform.machine().lower()
        arch_name = "arm64" if "arm" in arch or "aarch64" in arch else "amd64"
        filename = f"frpc_linux_{arch_name}_{version}"
    
    frpc_path = os.path.join(gradio_path, filename)
    
    print(f"📥 frpc dosyası indiriliyor: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(frpc_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Unix sistemlerinde çalıştırma izni ver
        if system != "windows":
            os.chmod(frpc_path, 0o755)
        
        print(f"✅ frpc dosyası başarıyla indirildi: {frpc_path}")
        return True
    
    except Exception as e:
        print(f"❌ İndirme sırasında hata oluştu: {e}")
        return False

def fix_gradio_share():
    """Gradio paylaşım özelliğini düzeltir"""
    success = download_frpc()
    
    if success:
        print("✅ Gradio paylaşım özelliği hazır!")
        print("   Şimdi uygulamayı `python main.py --share` komutuyla çalıştırabilirsiniz.")
        return True
    else:
        print("❌ Gradio paylaşım özelliği kurulamadı.")
        print("   Uygulamayı sadece yerel modda `python main.py` komutuyla çalıştırabilirsiniz.")
        return False

if __name__ == "__main__":
    print("🛠️ Gradio Paylaşım Özelliği Onarım Aracı")
    fix_gradio_share()
