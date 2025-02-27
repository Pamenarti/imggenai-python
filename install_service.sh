#!/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}AI Görsel Oluşturma - Sistem Hizmeti Kurulum Aracı${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Root yetkisi kontrolü
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Bu betik yönetici (sudo) haklarıyla çalıştırılmalıdır.${NC}"
  echo "Lütfen 'sudo $0' komutunu kullanın."
  exit 1
fi

# Çalışma dizinini al
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_DIR="${SCRIPT_DIR}"

# Kullanıcı adını belirle
USERNAME=$(logname || echo $SUDO_USER)
if [ -z "$USERNAME" ]; then
  echo -e "${RED}Kullanıcı adı belirlenemedi!${NC}"
  echo "Lütfen kullanıcı adınızı girin:"
  read -r USERNAME
fi

echo -e "${BLUE}Kurulum bilgileri:${NC}"
echo -e "Uygulama dizini: ${YELLOW}${APP_DIR}${NC}"
echo -e "Kullanıcı: ${YELLOW}${USERNAME}${NC}"
echo

# Servis dosyası oluştur
SERVICE_NAME="ai-image-generator"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Servis portu
echo -e "${BLUE}Web arayüzü için port numarası (varsayılan: 7860):${NC}"
read -r PORT_NUMBER
if [ -z "$PORT_NUMBER" ]; then
  PORT_NUMBER=7860
fi

# Düşük bellek modu
echo -e "${BLUE}Düşük bellek modu aktifleştirilsin mi? (e/H):${NC}"
read -r USE_LOW_MEMORY
if [[ $USE_LOW_MEMORY =~ ^[Ee] ]]; then
  LOW_MEMORY_FLAG="--low-memory"
else
  LOW_MEMORY_FLAG=""
fi

# İnternet üzerinden paylaşım
echo -e "${BLUE}İnternet üzerinden paylaşım aktifleştirilsin mi? (e/H):${NC}"
read -r USE_SHARE
if [[ $USE_SHARE =~ ^[Ee] ]]; then
  SHARE_FLAG="--share"
else
  SHARE_FLAG=""
fi

echo -e "${BLUE}Servis dosyası oluşturuluyor...${NC}"

# Servis dosyası içeriği
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=AI Görsel Oluşturma Servisi
After=network.target

[Service]
User=${USERNAME}
WorkingDirectory=${APP_DIR}
ExecStart=/bin/bash -c "source ${APP_DIR}/venv/bin/activate && python ${APP_DIR}/main.py --port ${PORT_NUMBER} ${LOW_MEMORY_FLAG} ${SHARE_FLAG}"
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=ai-image-generator
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Servis yetkileri düzenle
chmod 644 "$SERVICE_FILE"

# Systemd yapılandırmasını yenile
systemctl daemon-reload

# Servisi etkinleştir ve başlat
echo -e "${BLUE}Servis etkinleştiriliyor...${NC}"
systemctl enable "$SERVICE_NAME"

echo -e "${GREEN}Servis başlatılıyor...${NC}"
systemctl start "$SERVICE_NAME"

# Servis durumunu kontrol et
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
  echo -e "${GREEN}✅ Servis başarıyla kuruldu ve çalışıyor!${NC}"
  echo -e "Web arayüzüne şu adreslerden erişebilirsiniz:"
  echo -e "- Yerel erişim: ${BLUE}http://localhost:${PORT_NUMBER}${NC}"
  echo -e "- Ağ erişimi: ${BLUE}http://$(hostname -I | awk '{print $1}'):${PORT_NUMBER}${NC}"
  
  if [[ $USE_SHARE =~ ^[Ee] ]]; then
    echo -e "- İnternet erişimi: Servis loglarında gösterilen URL'yi kullanın."
    echo -e "  Log dosyasını görüntülemek için: ${YELLOW}journalctl -u ${SERVICE_NAME} -f${NC}"
  fi
else
  echo -e "${RED}❌ Servis başlatılamadı.${NC}"
  echo -e "Lütfen şu komutla hata mesajlarını kontrol edin: ${YELLOW}journalctl -u ${SERVICE_NAME} -xe${NC}"
fi

echo -e "\n${BLUE}Servis Yönetimi Komutları:${NC}"
echo -e "- Servisi başlatmak için: ${YELLOW}sudo systemctl start ${SERVICE_NAME}${NC}"
echo -e "- Servisi durdurmak için: ${YELLOW}sudo systemctl stop ${SERVICE_NAME}${NC}"
echo -e "- Servis durumunu kontrol etmek için: ${YELLOW}sudo systemctl status ${SERVICE_NAME}${NC}"
echo -e "- Servis loglarını görüntülemek için: ${YELLOW}journalctl -u ${SERVICE_NAME} -f${NC}"