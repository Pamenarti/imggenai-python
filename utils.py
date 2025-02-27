import torch
import platform
import os
import psutil
import socket
import logging
from datetime import datetime

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_system_info():
    """Sistem donanım bilgilerini kontrol eder ve hangi işlemcinin kullanıldığını bildirir."""
    
    info = {
        "system": platform.system(),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "gpu_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() and torch.cuda.device_count() > 0 else "Yok",
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2)
    }
    
    # GPU bellek bilgilerini al
    if info["gpu_available"]:
        try:
            gpu_mem_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_mem_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            gpu_mem_reserved = torch.cuda.memory_reserved(0) / (1024**3)
            
            info["gpu_memory_total"] = f"{gpu_mem_total:.2f} GB"
            info["gpu_memory_used"] = f"{gpu_mem_allocated:.2f} GB"
            info["gpu_memory_reserved"] = f"{gpu_mem_reserved:.2f} GB"
        except Exception as e:
            logger.error(f"GPU bellek bilgisi alınamadı: {e}")
    
    # Nvidia-smi kullanarak ekstra bilgiler al
    try:
        if info["gpu_available"]:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # GPU sıcaklığı
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            info["gpu_temp"] = f"{temp}°C"
            
            # GPU kullanımı
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            info["gpu_util"] = f"{util.gpu}%"
            
            pynvml.nvmlShutdown()
    except:
        pass  # Nvidia-smi mevcut değilse sessizce devam et
    
    # Bilgileri logla
    logger.info(f"Sistem kontrolü: {'GPU mevcut: ' + info['device_name'] if info['gpu_available'] else 'GPU yok'}")
    
    # Kullanılacak cihaz bilgisi
    if info["gpu_available"]:
        logger.info(f"PyTorch GPU kullanacak: {info['device_name']}")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        logger.info("PyTorch MPS (Apple Silicon) kullanacak")
        info["device_name"] = "Apple M-Series (MPS)"
        info["gpu_available"] = True
    else:
        logger.info("PyTorch CPU kullanacak")
    
    return info

def display_server_info():
    """Sunucu bilgilerini gösterir"""
    server_info = {
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()) if platform.system() != "Darwin" else "127.0.0.1",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    }
    
    logger.info(f"Sunucu: {server_info['hostname']} ({server_info['ip']})")
    
    return server_info

def format_time(seconds):
    """Saniye cinsinden süreyi formatlı bir metne dönüştürür"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}s {minutes}d {seconds}s"
    elif minutes > 0:
        return f"{minutes}d {seconds}s"
    else:
        return f"{seconds}s"

def configure_environment():
    """Çalışma ortamı için optimum ayarları yapılandırır"""
    # CUDA cihazı varsa optimizasyon yap
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True  # Hızlı evrişim algoritması seçimi
        torch.backends.cuda.matmul.allow_tf32 = True  # TF32 formatına izin ver
        torch.backends.cudnn.allow_tf32 = True
    
    # Çevre değişkenlerini ayarla
    os.environ["PYTHONHASHSEED"] = str(42)  # Deterministik hash
    os.environ["TOKENIZERS_PARALLELISM"] = "true"  # Tokenizer paralelliği
    
    # HuggingFace önbellek dizinini ayarla
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
    os.environ["TRANSFORMERS_CACHE"] = cache_dir
    os.environ["HF_HOME"] = cache_dir
    
    return True

# Sistem bilgisini yazdırmak için test
if __name__ == "__main__":
    info = check_system_info()
    
    print("\n=== Sistem Bilgileri ===")
    print(f"İşletim Sistemi: {info['system']}")
    print(f"Python Sürümü: {info['python_version']}")
    print(f"PyTorch Sürümü: {info['torch_version']}")
    print(f"CPU Çekirdek Sayısı: {info['cpu_count']}")
    print(f"Bellek: {info['memory_gb']} GB")
    
    print("\n=== GPU Bilgileri ===")
    if info['gpu_available']:
        print(f"GPU: {info['device_name']}")
        print(f"GPU Sayısı: {info['device_count']}")
        if "gpu_memory_total" in info:
            print(f"GPU Bellek: {info['gpu_memory_used']} / {info['gpu_memory_total']}")
        if "gpu_temp" in info:
            print(f"GPU Sıcaklığı: {info['gpu_temp']}")
        if "gpu_util" in info:
            print(f"GPU Kullanımı: {info['gpu_util']}")
    else:
        print("GPU bulunamadı, CPU kullanılacak")
        
    print("\n=== Sunucu Bilgileri ===")
    server_info = display_server_info()
    print(f"Sunucu Adı: {server_info['hostname']}")
    print(f"IP Adresi: {server_info['ip']}")
    print(f"Çalışma Süresi: {server_info['uptime']}")
