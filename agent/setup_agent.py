#!/usr/bin/env python3
"""
Setup script for Remote PC Agent
Configures the agent and installs it as a system service
"""

import os
import sys
import json
import secrets
import socket
import platform
from pathlib import Path

CONFIG_DIR = Path.home() / '.remote-pc-agent'
CONFIG_FILE = CONFIG_DIR / 'config.json'
TOKEN_FILE = CONFIG_DIR / 'token'

def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def setup_config():
    """Setup initial configuration"""
    print("=== Remote PC Agent Setup ===\n")

    # Create config directory
    CONFIG_DIR.mkdir(exist_ok=True)

    # Get configuration from user
    pc_name = input(f"Nombre de esta PC [{socket.gethostname()}]: ").strip()
    if not pc_name:
        pc_name = socket.gethostname()

    port = input("Puerto [9876]: ").strip()
    if not port:
        port = 9876
    else:
        port = int(port)

    # Generate or input token
    use_existing_token = input("¿Tienes un token existente? (s/N): ").strip().lower()
    if use_existing_token == 's':
        token = input("Ingresa el token: ").strip()
    else:
        token = generate_token()
        print(f"\n🔑 Token generado: {token}")
        print("⚠️  GUARDA ESTE TOKEN - lo necesitarás para conectar el servidor\n")

    # Save configuration
    config = {
        'pc_name': pc_name,
        'port': port
    }

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    with open(TOKEN_FILE, 'w') as f:
        f.write(token)

    os.chmod(TOKEN_FILE, 0o600)

    print(f"\n✅ Configuración guardada en {CONFIG_DIR}")
    print(f"   - Nombre PC: {pc_name}")
    print(f"   - Puerto: {port}")
    print(f"   - Token: guardado en {TOKEN_FILE}")

    return config, token

def install_service():
    """Install agent as a system service"""
    system = platform.system()
    agent_path = Path(__file__).parent / 'agent.py'

    print(f"\n📦 Instalando servicio para {system}...")

    if system == 'Darwin':  # macOS
        install_macos_service(agent_path)
    elif system == 'Windows':
        install_windows_service(agent_path)
    elif system == 'Linux':
        install_linux_service(agent_path)
    else:
        print(f"⚠️  Sistema {system} no soportado para instalación automática")
        print(f"   Ejecuta manualmente: python {agent_path}")

def install_macos_service(agent_path):
    """Install as macOS LaunchAgent"""
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.remotepc.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{agent_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{Path.home()}/Library/Logs/remote-pc-agent.log</string>
    <key>StandardErrorPath</key>
    <string>{Path.home()}/Library/Logs/remote-pc-agent-error.log</string>
</dict>
</plist>
'''

    plist_path = Path.home() / 'Library/LaunchAgents/com.remotepc.agent.plist'
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    with open(plist_path, 'w') as f:
        f.write(plist_content)

    print(f"✅ LaunchAgent creado en {plist_path}")
    print("\nPara iniciar el servicio:")
    print(f"  launchctl load {plist_path}")
    print(f"  launchctl start com.remotepc.agent")
    print("\nPara detener el servicio:")
    print(f"  launchctl stop com.remotepc.agent")
    print(f"  launchctl unload {plist_path}")

def install_windows_service(agent_path):
    """Install as Windows service"""
    print("\n📝 Para Windows, crea un Scheduled Task:")
    print("1. Abre 'Task Scheduler'")
    print("2. Create Task > General:")
    print("   - Name: Remote PC Agent")
    print("   - Run whether user is logged on or not")
    print("   - Run with highest privileges")
    print("3. Triggers > New:")
    print("   - Begin: At startup")
    print("4. Actions > New:")
    print(f"   - Program: {sys.executable}")
    print(f"   - Arguments: {agent_path}")
    print("5. Settings:")
    print("   - Allow task to be run on demand")
    print("   - If task fails, restart every: 1 minute")

    # Create a batch file for easy starting
    batch_path = Path.home() / 'Desktop/start_remote_agent.bat'
    with open(batch_path, 'w') as f:
        f.write(f'@echo off\n"{sys.executable}" "{agent_path}"\npause')

    print(f"\n✅ Creado: {batch_path}")
    print("   Ejecuta este archivo para iniciar el agente manualmente")

def install_linux_service(agent_path):
    """Install as Linux systemd service"""
    service_content = f'''[Unit]
Description=Remote PC Control Agent
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
ExecStart={sys.executable} {agent_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''

    service_path = '/etc/systemd/system/remote-pc-agent.service'

    print(f"\n📝 Contenido del servicio systemd:")
    print(service_content)
    print(f"\nPara instalar, ejecuta como root:")
    print(f"  sudo nano {service_path}")
    print("  (pega el contenido de arriba)")
    print("\nLuego:")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable remote-pc-agent")
    print("  sudo systemctl start remote-pc-agent")

def main():
    # Setup configuration
    config, token = setup_config()

    # Ask about service installation
    install = input("\n¿Quieres instalar el agente como servicio? (S/n): ").strip().lower()
    if install != 'n':
        install_service()

    print("\n" + "="*50)
    print("✅ SETUP COMPLETADO")
    print("="*50)
    print(f"\n🔑 TOKEN: {token}")
    print("\n⚠️  Guarda este token en un lugar seguro!")
    print("   Lo necesitarás para configurar el servidor.\n")
    print("Para iniciar el agente manualmente:")
    print(f"  python {Path(__file__).parent / 'agent.py'}\n")

if __name__ == '__main__':
    main()
