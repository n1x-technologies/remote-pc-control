#!/bin/bash
# Quick start script for Control Server

cd "$(dirname "$0")/../server"

echo "🚀 Iniciando servidor de control..."
echo ""
echo "Panel web disponible en: http://localhost:8080"
echo ""

python3 server.py
