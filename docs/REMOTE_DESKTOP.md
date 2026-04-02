# Configuración de Escritorio Remoto

Además de ejecutar comandos, puedes controlar visualmente las PCs remotas con escritorio remoto.

## Opción 1: VNC sobre Tailscale (Recomendado)

VNC funciona excelente sobre Tailscale ya que la conexión está encriptada.

### macOS (como servidor VNC)

macOS incluye un servidor VNC integrado:

1. **Habilitar Screen Sharing:**
   ```
   System Preferences > Sharing > Screen Sharing
   ```

2. **Configurar acceso VNC:**
   ```
   Computer Settings... > VNC viewers may control screen with password
   ```
   Establece una contraseña.

3. **Conectar desde otra PC:**
   ```bash
   # Desde macOS
   open vnc://TAILSCALE_IP

   # Desde Windows/Linux (usa un cliente VNC como RealVNC, TightVNC)
   # Conecta a: TAILSCALE_IP:5900
   ```

### Windows (como servidor RDP)

Windows incluye Remote Desktop Protocol (RDP):

1. **Habilitar RDP:**
   ```
   Settings > System > Remote Desktop > Enable Remote Desktop
   ```

2. **Conectar desde otra PC:**

   **Desde Windows:**
   ```
   Start > Remote Desktop Connection
   IP: TAILSCALE_IP
   ```

   **Desde macOS:**
   ```bash
   # Instalar Microsoft Remote Desktop desde App Store
   # O usar cliente RDP alternativo
   open rdp://TAILSCALE_IP
   ```

   **Desde Linux:**
   ```bash
   # Instalar Remmina
   sudo apt install remmina remmina-plugin-rdp
   remmina
   # Conectar a TAILSCALE_IP:3389
   ```

### Linux (como servidor VNC)

```bash
# Ubuntu/Debian - Instalar x11vnc
sudo apt install x11vnc

# Crear contraseña
x11vnc -storepasswd

# Iniciar servidor VNC
x11vnc -usepw -display :0 -forever

# O usar vino (GNOME)
sudo apt install vino
gsettings set org.gnome.Vino require-encryption false
/usr/lib/vino/vino-server &
```

## Opción 2: Chrome Remote Desktop

Chrome Remote Desktop funciona bien con Tailscale:

1. **Instalar:** https://remotedesktop.google.com/
2. **Configurar en PC remota:** "Set up remote access"
3. **Conectar desde cualquier lugar:** https://remotedesktop.google.com/access

**Ventajas:**
- Funciona en todos los sistemas
- No requiere configuración de red
- Calidad de imagen adaptativa

**Desventajas:**
- Requiere cuenta Google
- Menos privado que VNC/RDP directo

## Opción 3: NoMachine

NoMachine es rápido y multiplataforma:

1. **Descargar:** https://www.nomachine.com/
2. **Instalar en todas las PCs**
3. **Conectar usando la IP Tailscale**

**Ventajas:**
- Muy rápido
- Transferencia de archivos integrada
- Gratis para uso personal

## Opción 4: SSH con X11 Forwarding (Linux/macOS)

Para aplicaciones gráficas específicas (no escritorio completo):

```bash
# Conectar con X11 forwarding
ssh -X user@TAILSCALE_IP

# Ejecutar aplicación gráfica
firefox &
```

## Integración con Remote PC Control

Puedes agregar botones para iniciar escritorio remoto en el panel web:

```python
# En server.py, agregar endpoint
@app.route('/api/client/<name>/vnc-url')
def get_vnc_url(name):
    pc = manager.get_client(name)
    if not pc:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({
        'vnc_url': f'vnc://{pc.host}:5900',
        'rdp_url': f'rdp://{pc.host}:3389'
    })
```

## Automatización con Scripts

### Script para iniciar VNC en macOS

Agregar al agente:

```python
@app.route('/start-vnc', methods=['POST'])
@require_auth
def start_vnc():
    """Start VNC server on macOS"""
    try:
        if platform.system() == 'Darwin':
            # Enable Screen Sharing
            os.system('sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist')
            return jsonify({'message': 'VNC started'})
        else:
            return jsonify({'error': 'Not supported on this platform'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Script para Wake-on-LAN

Si quieres despertar una PC que está apagada:

```python
# wol.py
import socket

def wake_on_lan(mac_address):
    """Send magic packet to wake PC"""
    mac_bytes = bytes.fromhex(mac_address.replace(':', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(magic_packet, ('<broadcast>', 9))
    sock.close()

# Uso
wake_on_lan('AA:BB:CC:DD:EE:FF')
```

## Comparación de Opciones

| Solución | Velocidad | Calidad | Multiplataforma | Setup |
|----------|-----------|---------|-----------------|-------|
| VNC | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | Fácil |
| RDP (Windows) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | Muy fácil |
| Chrome Remote Desktop | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | Muy fácil |
| NoMachine | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | Fácil |
| SSH X11 | ⭐⭐ | ⭐⭐ | Linux/macOS | Medio |

## Recomendaciones

**Para Windows → Windows:**
- Usa RDP nativo (mejor calidad)

**Para macOS → macOS:**
- Usa Screen Sharing nativo (integrado)

**Para Linux → cualquiera:**
- Usa NoMachine (mejor performance)

**Para acceso móvil:**
- Chrome Remote Desktop (funciona en apps móviles)

**Para máxima seguridad:**
- VNC sobre Tailscale (todo encriptado)

## Tips de Performance

1. **Ajusta la calidad:**
   - Reduce resolución/colores en conexiones lentas
   - Usa compresión cuando sea posible

2. **Usa codec moderno:**
   - NoMachine usa codecs modernos (H.264)
   - RDP en Windows 10+ usa RemoteFX

3. **Desactiva efectos visuales:**
   - En Windows: System > Remote Desktop > Advanced
   - En macOS: Reduce transparencias y animaciones

4. **Monitorea el bandwidth:**
   ```bash
   # Ver uso de red
   python3 control.py stats mi-pc-casa
   ```

## Troubleshooting

### No puedo conectar al VNC/RDP

1. Verifica que el servicio esté corriendo:
   ```bash
   # macOS (VNC)
   sudo launchctl list | grep screensharing

   # Windows (RDP)
   # Services > Remote Desktop Services

   # Linux (VNC)
   ps aux | grep vnc
   ```

2. Verifica el puerto:
   ```bash
   # Desde tu PC de control
   nc -zv TAILSCALE_IP 5900  # VNC
   nc -zv TAILSCALE_IP 3389  # RDP
   ```

3. Verifica firewall:
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

   # Windows
   # Firewall > Advanced Settings > Inbound Rules
   ```

### Conexión lenta

1. Reduce la calidad de imagen en el cliente
2. Verifica el ping a través de Tailscale:
   ```bash
   tailscale ping NOMBRE_DE_PC
   ```
3. Usa NoMachine (mejor compresión)
4. Considera usar solo SSH para tareas sin GUI
