#!/bin/bash

echo "🔧 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

echo "⬇️ Instalando dependências do sistema..."
sudo apt update
sudo apt install -y ffmpeg libsm6 libxext6

echo "⬇️ Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup concluído! Ative o ambiente com:"
echo "source venv/bin/activate"
