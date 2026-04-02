#!/bin/bash
# Install script for Remote PC Agent (macOS/Linux)

set -e

echo "========================================"
echo "Remote PC Control - Agent Installation"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "   Instálalo desde: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Check Tailscale
if ! command -v tailscale &> /dev/null; then
    echo "⚠️  Tailscale no está instalado"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Para macOS, ejecuta:"
        echo "  brew install tailscale"
        echo "  sudo tailscale up"
    else
        echo "Para Linux, visita: https://tailscale.com/download"
    fi
    echo ""
    read -p "¿Continuar sin Tailscale? (s/N): " continue_without_tailscale
    if [[ ! "$continue_without_tailscale" =~ ^[sS]$ ]]; then
        exit 1
    fi
else
    echo "✅ Tailscale instalado"
    TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "no configurado")
    echo "   IP Tailscale: $TAILSCALE_IP"
fi

echo ""
echo "📦 Instalando dependencias Python..."
pip3 install -r ../requirements.txt

echo ""
echo "⚙️  Configurando agente..."
cd ../agent
python3 setup_agent.py

echo ""
echo "========================================"
echo "✅ INSTALACIÓN COMPLETADA"
echo "========================================"
echo ""
echo "Para iniciar el agente:"
echo "  cd $(pwd)"
echo "  python3 agent.py"
echo ""
echo "O configura el servicio del sistema para inicio automático."
echo ""
