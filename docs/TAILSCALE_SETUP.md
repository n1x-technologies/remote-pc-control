# Configuración de Tailscale

Tailscale crea una red VPN privada (mesh network) entre tus dispositivos que funciona incluso si están detrás de NAT o firewalls. Es la clave para tener acceso permanente a tus PCs remotas.

## ¿Por qué Tailscale?

- ✅ **Siempre conectado**: Las PCs permanecen accesibles 24/7
- ✅ **Funciona en cualquier red**: Detrás de NAT, firewalls, etc.
- ✅ **Seguro**: Encriptación WireGuard de extremo a extremo
- ✅ **Sin IP pública**: No necesitas abrir puertos ni tener IP fija
- ✅ **Multiplataforma**: Windows, macOS, Linux, iOS, Android
- ✅ **Gratis**: Para uso personal (hasta 100 dispositivos)

## Instalación

### macOS

```bash
# Con Homebrew
brew install tailscale

# Iniciar Tailscale
sudo tailscale up

# Ver tu IP en la Tailnet
tailscale ip -4
```

### Windows

1. Descarga desde: https://tailscale.com/download/windows
2. Instala y ejecuta
3. Inicia sesión con tu cuenta (Google, Microsoft, etc.)
4. ¡Listo!

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4
```

## Configuración Inicial

1. **Crear cuenta**: Ve a https://login.tailscale.com y crea una cuenta
2. **Instalar en todos los dispositivos**: Instala Tailscale en tu PC de control y en todas las PCs remotas
3. **Conectar todos**: En cada dispositivo, ejecuta `tailscale up` e inicia sesión
4. **Verificar**: Todos los dispositivos aparecerán en https://login.tailscale.com/admin/machines

## Obtener las IPs de tus dispositivos

### Desde la PC

```bash
# Ver tu IP
tailscale ip -4

# Ver todas las máquinas
tailscale status
```

### Desde el panel web

1. Ve a https://login.tailscale.com/admin/machines
2. Verás todas tus PCs con sus IPs Tailscale (formato: 100.x.x.x)

## Configuración Recomendada

### 1. Desactivar expiración de claves

Por defecto, las claves expiran cada 180 días. Para PCs remotas desatendidas:

1. Ve a https://login.tailscale.com/admin/machines
2. Haz clic en cada máquina
3. Click en "Disable key expiry"

### 2. Habilitar SSH (opcional)

Tailscale incluye SSH integrado:

```bash
# En cada PC
tailscale up --ssh
```

Luego puedes conectarte desde cualquier otra PC en tu Tailnet:

```bash
ssh user@nombre-de-pc
```

### 3. MagicDNS

Tailscale asigna nombres DNS a tus máquinas. Habilítalo en:
https://login.tailscale.com/admin/dns

Ejemplo: `mi-pc.tail-scale.ts.net` en lugar de `100.101.102.103`

### 4. Subnet routing (avanzado)

Si quieres acceder a toda la red local de una PC remota:

```bash
# En la PC remota (macOS/Linux)
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
tailscale up --advertise-routes=192.168.1.0/24

# Aprobar en el panel web
# https://login.tailscale.com/admin/machines -> máquina -> Edit route settings
```

## Uso con Remote PC Control

### 1. Instalar y configurar Tailscale en todas las PCs

```bash
# En cada PC remota
sudo tailscale up
tailscale ip -4  # Guarda esta IP
```

### 2. Agregar PCs al servidor de control

```bash
# En tu PC de control
python control.py add mi-pc-casa 100.101.102.103 --token TU_TOKEN
python control.py add mi-pc-trabajo 100.101.102.104 --token TU_TOKEN
```

### 3. Verificar conexión

```bash
python control.py list
```

Deberías ver todas tus PCs como "Online" 🟢

## Troubleshooting

### No puedo conectarme a una PC

1. Verifica que Tailscale esté corriendo:
   ```bash
   tailscale status
   ```

2. Verifica que el agente esté corriendo en la PC remota:
   ```bash
   # Debería responder
   curl http://TAILSCALE_IP:9876/ping
   ```

3. Verifica que la PC remota esté en tu Tailnet:
   ```bash
   tailscale ping NOMBRE_DE_PC
   ```

### La conexión se cae

1. Desactiva la expiración de claves (ver arriba)
2. Verifica que Tailscale esté configurado para iniciar al arrancar
3. En macOS: `launchctl list | grep tailscale`
4. En Windows: Task Manager > Startup > Tailscale

### Firewall bloqueando conexiones

Tailscale normalmente no tiene problemas con firewalls, pero si tienes problemas:

1. Asegúrate de que Tailscale tenga permiso en el firewall del sistema
2. Abre el puerto 9876 (agente) solo para la Tailnet:
   - macOS/Linux: usa `pf` o `iptables`
   - Windows: Firewall > Reglas de entrada

## Recursos

- Documentación oficial: https://tailscale.com/kb/
- Panel de administración: https://login.tailscale.com/admin/
- Estado del servicio: https://status.tailscale.com/
