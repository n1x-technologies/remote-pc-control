# Guía Rápida de Uso

## Configuración Inicial (5 minutos)

### 1. Instalar Tailscale en todas las PCs

**macOS:**
```bash
brew install tailscale
sudo tailscale up
```

**Windows:**
1. Descarga: https://tailscale.com/download/windows
2. Instala e inicia sesión

**Anota las IPs Tailscale de cada PC:**
```bash
tailscale ip -4
```

### 2. Instalar el agente en PCs remotas

En cada PC que quieras controlar:

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/remote-pc-control.git
cd remote-pc-control

# Instalar
chmod +x scripts/install_agent.sh
./scripts/install_agent.sh
```

Windows: ejecuta `scripts\install_agent.bat`

**¡IMPORTANTE!** Guarda el token que se genera.

### 3. Configurar el servidor de control

En tu PC desde donde quieres controlar:

```bash
cd remote-pc-control
pip3 install -r requirements.txt

# Agregar PCs remotas
cd server
python3 control.py add mi-pc-casa 100.101.102.103 --token TOKEN_DEL_AGENTE
python3 control.py add mi-laptop 100.101.102.104 --token TOKEN_DEL_AGENTE

# Verificar
python3 control.py list
```

## Uso Diario

### Panel Web (Recomendado)

```bash
cd server
python3 server.py
```

Abre en tu navegador: http://localhost:8080

Desde el panel puedes:
- 📊 Ver estado de todas las PCs
- 💻 Ver CPU, RAM, Disco en tiempo real
- 🔧 Ejecutar comandos
- 🔄 Reiniciar PCs
- ⚡ Apagar PCs
- 📈 Ver procesos

### CLI (Línea de comandos)

```bash
# Ver todas las PCs
python3 control.py list

# Ver información de una PC
python3 control.py info mi-pc-casa

# Ver estadísticas en tiempo real
python3 control.py stats mi-pc-casa

# Ejecutar comando
python3 control.py exec mi-pc-casa "ls -la"
python3 control.py exec mi-laptop "dir"

# Subir archivo
python3 control.py upload mi-pc-casa archivo.txt /home/user/archivo.txt

# Descargar archivo
python3 control.py download mi-pc-casa /home/user/doc.pdf ./doc.pdf

# Ver procesos
python3 control.py processes mi-pc-casa

# Reiniciar
python3 control.py reboot mi-pc-casa

# Apagar
python3 control.py shutdown mi-pc-casa
```

## Ejemplos Prácticos

### Monitorear varias PCs

```bash
# Ver estado de todas
python3 control.py list

# Ejecutar el mismo comando en varias PCs
for pc in mi-pc-casa mi-laptop mi-pc-trabajo; do
    echo "=== $pc ==="
    python3 control.py exec $pc "uptime"
done
```

### Backup automático

```bash
#!/bin/bash
# backup.sh - Descargar backups de todas las PCs

BACKUP_DIR=~/backups/$(date +%Y-%m-%d)
mkdir -p $BACKUP_DIR

# Desde mi-pc-casa
python3 control.py download mi-pc-casa \
    /home/user/documents.zip \
    $BACKUP_DIR/casa-documents.zip

# Desde mi-laptop
python3 control.py download mi-laptop \
    /Users/user/important.zip \
    $BACKUP_DIR/laptop-important.zip

echo "✅ Backups guardados en $BACKUP_DIR"
```

### Actualizar todas las PCs

```bash
#!/bin/bash
# update_all.sh

COMPUTERS=("mi-pc-casa" "mi-laptop" "mi-pc-trabajo")

for pc in "${COMPUTERS[@]}"; do
    echo "Actualizando $pc..."

    # macOS
    python3 control.py exec $pc "brew update && brew upgrade"

    # O para Linux:
    # python3 control.py exec $pc "sudo apt update && sudo apt upgrade -y"
done

echo "✅ Todas las PCs actualizadas"
```

### Reiniciar todas las PCs a cierta hora

```bash
#!/bin/bash
# reboot_schedule.sh
# Agregar a cron: 0 3 * * * /path/to/reboot_schedule.sh

COMPUTERS=("mi-pc-casa" "mi-laptop")

for pc in "${COMPUTERS[@]}"; do
    echo "Programando reinicio de $pc..."
    python3 control.py reboot $pc
done
```

### Script de monitoreo

```bash
#!/bin/bash
# monitor.sh - Alertar si CPU/RAM muy alta

THRESHOLD=90

for pc in mi-pc-casa mi-laptop; do
    stats=$(python3 control.py stats $pc)

    cpu=$(echo "$stats" | grep CPU | awk '{print $2}' | tr -d '%')
    ram=$(echo "$stats" | grep RAM | awk '{print $2}' | tr -d '%')

    if (( $(echo "$cpu > $THRESHOLD" | bc -l) )); then
        echo "⚠️  ALERTA: $pc tiene CPU al ${cpu}%"
        # Aquí puedes agregar notificación por email, Slack, etc.
    fi

    if (( $(echo "$ram > $THRESHOLD" | bc -l) )); then
        echo "⚠️  ALERTA: $pc tiene RAM al ${ram}%"
    fi
done
```

### Ejecutar script remoto

```bash
# 1. Subir script
python3 control.py upload mi-pc-casa ./script.sh /tmp/script.sh

# 2. Dar permisos
python3 control.py exec mi-pc-casa "chmod +x /tmp/script.sh"

# 3. Ejecutar
python3 control.py exec mi-pc-casa "/tmp/script.sh"
```

## Acceso desde el Móvil

### Opción 1: Instalar Tailscale en tu móvil

1. Instala la app Tailscale (iOS/Android)
2. Inicia sesión
3. Accede al panel web desde el móvil: `http://TAILSCALE_IP_DE_TU_PC:8080`

### Opción 2: Túnel SSH + Panel Web

```bash
# Desde tu móvil (con app SSH)
ssh -L 8080:localhost:8080 user@tu-pc-control

# Luego abre en el navegador del móvil:
# http://localhost:8080
```

## Automatización con Cron

### En tu PC de control

```bash
# Editar crontab
crontab -e

# Agregar tareas
# Backup diario a las 2 AM
0 2 * * * cd /ruta/a/remote-pc-control/server && ./backup.sh

# Monitoreo cada 5 minutos
*/5 * * * * cd /ruta/a/remote-pc-control/server && ./monitor.sh

# Reinicio semanal (domingos a las 3 AM)
0 3 * * 0 cd /ruta/a/remote-pc-control/server && python3 control.py reboot mi-pc-casa
```

## Seguridad

### Cambiar el token

```bash
# En la PC remota
cd ~/.remote-pc-agent
echo "nuevo_token_seguro_aqui" > token

# Reiniciar agente
# (o reiniciar el servicio si está configurado)
```

### Usar HTTPS (producción)

Si quieres exponer el panel web fuera de Tailscale:

1. Usa un reverse proxy (nginx/caddy)
2. Configura certificado SSL
3. Usa autenticación adicional

```nginx
# nginx config
server {
    listen 443 ssl;
    server_name control.midominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    auth_basic "Control Panel";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://localhost:8080;
    }
}
```

## Tips

### Performance

- El panel web se actualiza automáticamente cada 5 segundos
- Usa el CLI para automatización (más rápido)
- Para muchas PCs (10+), aumenta el timeout en las requests

### Debugging

```bash
# Ver logs del agente
tail -f ~/.remote-pc-agent/agent.log

# Test manual de conectividad
curl http://TAILSCALE_IP:9876/ping

# Ver si el agente está corriendo
ps aux | grep agent.py
```

### Backup de configuración

```bash
# Guardar configuración de clientes
cp ~/.remote-pc-control/clients.json ~/backup/

# Restaurar
cp ~/backup/clients.json ~/.remote-pc-control/
```

## Próximos Pasos

1. **Configura servicios del sistema** para que los agentes inicien automáticamente
2. **Crea scripts de automatización** para tus tareas frecuentes
3. **Configura alertas** por email o Slack cuando algo falle
4. **Integra con otros servicios** (webhooks, IFTTT, etc.)
