# GPU Kullanımı Hakkında Bilgi

Bu yapay zeka görsel oluşturma yazılımı, yapay zeka modellerini çalıştırmak için GPU (ekran kartı) kullanır. Aşağıda sistemin GPU kullanımı hakkında sık sorulan sorular ve cevaplarını bulabilirsiniz:

## Hangi GPU Kullanılıyor?

Sistem, **çalıştığı bilgisayar/sunucudaki** GPU'yu kullanır:

1. **Yerel Çalıştırma**: Uygulamayı kendi bilgisayarınızda çalıştırıyorsanız, kendi bilgisayarınızın GPU'su kullanılır.

2. **Sunucu Üzerinde Çalıştırma**: Uygulama bir sunucuda çalışıyorsa ve siz web tarayıcısı üzerinden erişiyorsanız, sunucunun GPU'su kullanılır, sizin ekran kartınız kullanılmaz.

## GPU Gerekli mi?

Sistem CPU üzerinde de çalışabilir, ancak:

- GPU olmadan işlemler 10-20 kat daha yavaş olacaktır
- Görsel oluşturma süreleri dakikalar alabilir
- Büyük modeller yüksek RAM gereksinimi nedeniyle çalışmayabilir

## Minimum Gereksinimler

- **GPU ile**: NVIDIA CUDA destekli ekran kartı, en az 4GB VRAM
- **Sadece CPU ile**: En az 16GB RAM ve güçlü bir çoklu çekirdek işlemci

## GPU Performansı Nasıl Artırılır?

1. Sistem başlatıldığında otomatik olarak GPU'yu tespit eder
2. Görüntü oluşturma esnasında GPU belleğini verimli kullanmak için adım sayısını düşürebilirsiniz
3. Modeller ilk çalıştırmada GPU belleğine yüklenir ve sonraki kullanımlar için orada kalır

## GPU Bulunmadığında Ne Olur?

Eğer sistem GPU tespit edemezse:
1. Otomatik olarak CPU moduna geçer
2. Arayüzde bir uyarı gösterilir
3. İşlemler daha uzun sürer, ancak yine de çalışır
