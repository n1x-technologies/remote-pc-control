# Instrucciones de Configuración

## Repositorio Creado

✅ **Repositorio:** https://github.com/n1x-technologies/remote-pc-control

## Próximos Pasos

### 1. En las PCs que quieres controlar (remotas)

```bash
# Instalar Tailscale
# macOS:
brew install tailscale
sudo tailscale up

# Windows: descargar de https://tailscale.com/download

# Obtener IP de Tailscale
tailscale ip -4
# Guarda esta IP (ejemplo: 100.101.102.103)

# Clonar e instalar agente
git clone https://github.com/n1x-technologies/remote-pc-control.git
cd remote-pc-control

# macOS/Linux:
chmod +x scripts/install_agent.sh
./scripts/install_agent.sh

# Windows:
# Ejecutar scripts\install_agent.bat

# ⚠️ IMPORTANTE: Guarda el TOKEN que se genera
```

### 2. En tu PC de control

```bash
# Clonar repo
git clone https://github.com/n1x-technologies/remote-pc-control.git
cd remote-pc-control

# Instalar dependencias
pip3 install -r requirements.txt

# Agregar PCs remotas (usa el token y la IP de cada PC)
cd server
python3 control.py add mi-pc-casa 100.101.102.103 --token EL_TOKEN_QUE_GUARDASTE
python3 control.py add mi-laptop 100.101.102.104 --token OTRO_TOKEN

# Verificar que estén conectadas
python3 control.py list

# Iniciar panel web
python3 server.py
```

Abre tu navegador en: http://localhost:8080

### 3. Uso Básico

```bash
# Ver stats
python3 control.py stats mi-pc-casa

# Ejecutar comando
python3 control.py exec mi-pc-casa "ls -la"

# Subir archivo
python3 control.py upload mi-pc-casa archivo.txt /ruta/destino/archivo.txt

# Reiniciar
python3 control.py reboot mi-pc-casa
```

## Documentación Completa

- [Guía Rápida](docs/QUICK_START.md)
- [Configuración Tailscale](docs/TAILSCALE_SETUP.md)
- [Escritorio Remoto](docs/REMOTE_DESKTOP.md)

## Soporte

Si tienes problemas, revisa los logs:
- Agente: `~/.remote-pc-agent/agent.log`
- Verifica conectividad: `tailscale ping nombre-de-pc`
