# 🎨 AI Görsel Oluşturma Kullanım Kılavuzu

Bu kılavuz, AI Görsel Oluşturma yazılımının kullanımını açıklar ve entegre edilen özel modellerin en iyi şekilde kullanılması için ipuçları sunar.

## 📋 İçindekiler

- [Genel Kullanım](#genel-kullanım)
- [Özel Modeller](#özel-modeller)
- [LoRA Adaptasyonları](#lora-adaptasyonları)
- [İş Akışları](#iş-akışları)
- [Gelişmiş İpuçları](#gelişmiş-i̇puçları)

## 🚀 Genel Kullanım

### Başlatma

Yazılımı çalıştırmak için:

```bash
# Normal kullanım
./run.sh

# Düşük bellek sistemler için
./run.sh --low-memory

# İnternet üzerinden paylaşmak için
./run.sh --share
```

### İlk Model İndirme

İlk kullanımda modeller otomatik olarak indirilir. Bu işlem birkaç dakika sürebilir. Tüm modelleri önceden indirmek için:

```bash
./run.sh --download-models
```

## 🔮 Özel Modeller

Sisteme entegre edilen özel modeller:

### 1. Pony Realism v2.1 ve v2.2

**En İyi Olduğu Alanlar:**
- Foto-gerçekçi insan portreleri
- Detaylı manzara fotoğrafları
- Gerçekçi nesne görselleri

**Örnek Kullanım:**
```
a photorealistic portrait of a young woman with blue eyes, detailed skin texture, professional lighting, 8k
```

### 2. Flux Uncensored

**En İyi Olduğu Alanlar:**
- Yaratıcı dijital sanat
- Fantastik temalar
- Anime tarzı görseller

**Örnek Kullanım:**
```
digital art of a futuristic cyberpunk city, neon lights, rainy night, detailed, vibrant colors
```

## 🎭 LoRA Adaptasyonları

### Tatsumaki (One Punch Man)

One Punch Man anime/manga serisinden Tatsumaki karakterini görselleştirmek için LoRA adaptasyonu.

**Kullanım:**
1. "Metin → Görsel" sekmesinde LoRA açılır menüsünden "Tatsumaki (One Punch Man)" seçin
2. Promptunuzu girin (karakter özelliklerini belirtmek zorunda değilsiniz, otomatik eklenecektir)

**Örnek Prompt:**
```
a character in a powerful pose, city background, anime style
```

## ⚙️ İş Akışları

### Basit İş Akışı

Temel görsel oluşturma işlemidir, verilen bir promptu farklı modellerle render eder.

### Stil Transferi

Aynı açıklamayı farklı sanatsal stillerde görselleştirir:
- Yağlıboya
- Anime
- Dijital sanat
- Suluboya
- Karakalem

### Gelişmiş Düzenleme

Bir görsel oluşturup farklı varyasyonlarını üretir:
- Detay artırma
- Dramatik aydınlatma
- Canlı renkler
- Koyu tonlar

## 💡 Gelişmiş İpuçları

### Daha İyi Görseller İçin

1. **Detaylı Açıklamalar Kullanın**: Görselinizi açıklarken mümkün olduğunca detaylı olun.
   ```
   "bir kedi" KÖTÜ
   "yakın çekim, detaylı, siyah bir kedinin portresi, yeşil gözler, stüdyo aydınlatması" İYİ
   ```

2. **Stil Belirtin**: İstediğiniz sanatsal stili belirtin.
   ```
   "yağlıboya", "dijital sanat", "anime", "fotoğraf", "hyperrealism" gibi
   ```

3. **Negatif Promptlar Kullanın**: İstemediğiniz öğeleri belirtebilirsiniz.
   ```
   "blur, low quality, distortion, yazı, text, watermark olmadan"
   ```

4. **Model Seçimini Doğru Yapın**:
   - Gerçekçi insan portreleri için → Pony Realism
   - Fantastik sanat için → Flux Uncensored
   - Genel amaçlı → Stable Diffusion v1.5

### GPU Bellek Optimizasyonu

1. **Diffusion Adımlarını Azaltın**: Düşük bellekli sistemlerde 20-30 adım yeterli olabilir
2. **Düşük Bellek Modunu Kullanın**: `--low-memory` parametresi ile çalıştırın
3. **Görüntü Çözünürlüğünü Düşürün**: Birçok modelde 512x512 çözünürlüklü görüntüler oluşturulur

## 📝 Sorun Giderme

- **Modeller İndirilemiyor**: İnternet bağlantınızı kontrol edin
- **GPU Bellek Hatası**: Düşük bellek modunu kullanın veya diffusion adımlarını azaltın
- **Görsel Oluşturma Çok Yavaş**: CPU modunda çalışıyor olabilirsiniz, NVIDIA GPU'ya sahip bir sistem kullanın
