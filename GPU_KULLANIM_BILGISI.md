# GPU Kullanımı ve Optimizasyon Rehberi

Bu dokümanda, görüntü üretimi sırasında GPU kullanımı ve optimizasyonu hakkında bilgiler yer almaktadır.

## GPU Gereksinimleri

Diffusion modelleri hesaplama açısından yoğun işlemlerdir ve GPU kullanımı, işlem süresini önemli ölçüde hızlandırır:

- **Minimum**: 4GB VRAM (düşük çözünürlük, düşük kalite)
- **Önerilen**: 8GB+ VRAM (512x512 görüntüler için)
- **Optimum**: 12GB+ VRAM (yüksek çözünürlük ve batch işlemler için)

## GPU Bellek Optimizasyonu Teknikleri

GPU belleğinden tasarruf etmek için aşağıdaki teknikleri kullanabilirsiniz:

### 1. Düşük Bellek Modu

Uygulama `--low-memory` parametresi ile başlatıldığında:

- Model parçaları CPU ve GPU arasında taşınır
- Uyarı: İşlem süresi uzar, ancak daha büyük modeller çalıştırılabilir

### 2. Precision Değişiklikleri

- **float16**: Varsayılan olarak CUDA GPU'larda kullanılır, bellek kullanımını yarıya indirir
- **float32**: CPU'da veya bazı işlerde daha yüksek doğruluk gerektiğinde kullanılır

### 3. Attention Slicing

Bellek tasarrufu sağlamak için dikkat katmanları bölünür:
```python
pipe.enable_attention_slicing()
```

### 4. VRAM Kullanımını İzleme

GPU bellek kullanımını izlemek için:

```python
# Mevcut VRAM kullanımı
print(f"Kullanılan: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
print(f"Önbelleğe alınan: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
```

### 5. xFormers Optimizasyonu

xFormers kullanımı bellek verimliliğini artırabilir:

```python
pipe.enable_xformers_memory_efficient_attention()
```

## GPU Seçenekleri İçin Tavsiyeler

| GPU Modeli | VRAM | Maksimum Çözünürlük | Tavsiye |
|------------|------|---------------------|---------|
| GTX 1650   | 4GB  | 512x512             | Düşük bellek modu kullanın |
| GTX 1060   | 6GB  | 512x768             | Batch size=1, adım sayısını azaltın |
| RTX 3060   | 12GB | 1024x1024           | Normal veya düşük bellek modu |
| RTX 4090   | 24GB | 2048x2048+          | Tam performans modları |

## CPU Kullanıcıları İçin

GPU olmadan, aşağıdaki optimizasyon teknikleri önerilir:

1. İşlem adımlarını azaltın (20-30 arası)
2. Düşük çözünürlük kullanın (256x256 veya 384x384)
3. Daha küçük modeller kullanın (örneğin, SD-1.5 vs SD-XL)
4. İşlem sırasında sabrınızı koruyun, sonuçlar yavaş alınacaktır

## Sistem Sorunları

- **CUDA Hataları**: Pytorch ve CUDA sürümlerinin uyumluluğunu kontrol edin
- **Yüksek CPU Kullanımı**: CPU önceliklendirme ayarlarını kontrol edin
- **Düşük GPU Kullanımı**: CPU darboğazı olabilir, sistem izleme araçlarıyla kontrol edin

Bu ayarlamalar, sistem kaynaklarınızı en verimli şekilde kullanmanızı sağlayacaktır.
