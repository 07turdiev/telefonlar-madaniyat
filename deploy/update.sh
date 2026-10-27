#!/usr/bin/env bash
# Serverdagi nusxani GitHub'dagi oxirgi versiyaga yangilaydi va xizmatni qayta ishga tushiradi.
# Loyiha egasi nomidan ishga tushiriladi:  bash deploy/update.sh
# Xizmat nomi boshqacha bo'lsa:            SERVICE=nom bash deploy/update.sh
set -euo pipefail

SERVICE="${SERVICE:-telefonlar}"
cd "$(dirname "$0")/.."

echo "== git pull"
git pull --ff-only

echo "== backend paketlari"
if command -v uv >/dev/null 2>&1; then
    uv pip install --quiet --python backend/.venv/bin/python -r backend/requirements.txt
else
    backend/.venv/bin/pip install --quiet -r backend/requirements.txt
fi

echo "== frontend build"
(cd frontend && npm ci --no-audit --no-fund --loglevel=error && npm run build)

echo "== xizmatni qayta ishga tushirish"
sudo systemctl restart "$SERVICE"
sleep 2
systemctl is-active "$SERVICE"
