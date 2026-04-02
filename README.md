# Remote PC Control

Sistema de administración remota para controlar múltiples PCs desde cualquier lugar del mundo.

## Características

- 🌐 **Conexión permanente** via Tailscale VPN
- 💻 **Multi-plataforma**: Windows y macOS
- 🔧 **Ejecución remota** de comandos y scripts
- 🖥️ **Escritorio remoto** (VNC/RDP)
- 📁 **Transferencia de archivos**
- 📊 **Monitoreo del sistema** en tiempo real
- 🔄 **Reinicio remoto**
- 🔐 **Conexión segura** y encriptada

## Arquitectura

```
┌─────────────────┐
│  Tu PC Control  │
│   (Servidor)    │
└────────┬────────┘
         │
    ┌────┴────┐ Tailscale VPN Mesh
    │         │
┌───▼───┐ ┌──▼────┐
│ PC #1 │ │ PC #2 │  ... más PCs
│Agent  │ │Agent  │
└───────┘ └───────┘
```

## Instalación Rápida

### 1. Instalar Tailscale (en todas las PCs)

**macOS:**
```bash
brew install tailscale
sudo tailscale up
```

**Windows:**
Descarga e instala desde: https://tailscale.com/download

### 2. Instalar el Agente (en PCs remotas)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/remote-pc-control.git
cd remote-pc-control

# Instalar dependencias
pip install -r requirements.txt

# Configurar e iniciar agente
cd agent
python setup_agent.py
```

### 3. Instalar el Servidor (en tu PC de control)

```bash
cd server
pip install -r requirements.txt
python server.py
```

## Uso

### Panel Web
Accede a `http://localhost:8080` para ver todas tus PCs conectadas.

### CLI
```bash
# Listar PCs conectadas
python control.py list

# Ejecutar comando remoto
python control.py exec <pc-name> "comando"

# Reiniciar PC
python control.py reboot <pc-name>

# Transferir archivo
python control.py upload <pc-name> archivo.txt /ruta/destino/

# Monitoreo en tiempo real
python control.py monitor <pc-name>
```

## Configuración

Edita `config.yaml` para personalizar:
- Puerto del servidor
- Intervalo de heartbeat
- Comandos permitidos
- Logs

## Seguridad

- ✅ Todo el tráfico va por Tailscale (WireGuard encryption)
- ✅ Autenticación por tokens
- ✅ Los agentes solo aceptan conexiones de IPs en la Tailnet
- ✅ Logs de todas las operaciones

## Requisitos

- Python 3.8+
- Tailscale instalado y configurado
- Permisos de administrador (para algunas operaciones)

## Licencia

MIT
