#!/bin/bash

echo "AI Görsel Üretme Uygulaması - Video Bağımlılıklarını Kuruyor"
echo "============================================================"

# FFmpeg kontrol
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg bulunamadı - kurulumu başlatılıyor"
    sudo apt-get update -y
    sudo apt-get install -y ffmpeg
else
    echo "FFmpeg zaten yüklü"
fi

# Python kütüphanelerini kur
echo "Python kütüphaneleri yükleniyor..."
pip install moviepy
pip install imageio
pip install imageio-ffmpeg

# MoviePy kurulumunu doğrula
echo "MoviePy kurulumu doğrulanıyor..."
python -c "from moviepy.editor import VideoClip; print('MoviePy kurulumu başarılı')" || echo "MoviePy kurulumunda sorun oluştu"

echo "Video bağımlılıkları kurulumu tamamlandı!"
echo "Artık ./main.py ile uygulamayı başlatabilirsiniz."
