#!/usr/bin/env python3
"""
Remote PC Control CLI
Command-line interface to control remote PCs
"""

import sys
import json
import requests
import argparse
from pathlib import Path
from tabulate import tabulate

CONFIG_FILE = Path.home() / '.remote-pc-control' / 'clients.json'

class RemotePC:
    def __init__(self, name, host, port, token):
        self.name = name
        self.host = host
        self.port = port
        self.token = token
        self.base_url = f'http://{host}:{port}'
        self.headers = {'Authorization': f'Bearer {token}'}

    def request(self, endpoint, method='GET', **kwargs):
        """Make a request to the agent"""
        url = f'{self.base_url}/{endpoint}'
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                timeout=30,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f'❌ Error connecting to {self.name}: {e}')
            return None

    def ping(self):
        """Check if PC is online"""
        response = self.request('ping')
        return response is not None

    def get_info(self):
        """Get system information"""
        response = self.request('info')
        return response.json() if response else None

    def get_stats(self):
        """Get real-time stats"""
        response = self.request('stats')
        return response.json() if response else None

    def execute(self, command, timeout=300):
        """Execute a command"""
        response = self.request(
            'execute',
            method='POST',
            json={'command': command, 'timeout': timeout}
        )
        return response.json() if response else None

    def reboot(self):
        """Reboot the system"""
        response = self.request('reboot', method='POST')
        return response.json() if response else None

    def shutdown(self):
        """Shutdown the system"""
        response = self.request('shutdown', method='POST')
        return response.json() if response else None

    def upload_file(self, local_path, remote_path):
        """Upload a file to the remote PC"""
        with open(local_path, 'rb') as f:
            files = {'file': f}
            data = {'path': remote_path}
            response = self.request(
                'upload',
                method='POST',
                files=files,
                data=data,
                headers={'Authorization': f'Bearer {self.token}'}  # Files upload needs explicit headers
            )
        return response.json() if response else None

    def download_file(self, remote_path, local_path):
        """Download a file from the remote PC"""
        response = self.request('download', params={'path': remote_path})
        if response:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return True
        return False

    def get_processes(self):
        """Get running processes"""
        response = self.request('processes')
        return response.json() if response else None

class ControlManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.clients = {}
        self.load_clients()

    def load_clients(self):
        """Load client configurations"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                data = json.load(f)
                for name, config in data.items():
                    self.clients[name] = RemotePC(
                        name,
                        config['host'],
                        config['port'],
                        config['token']
                    )

    def save_clients(self):
        """Save client configurations"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            name: {
                'host': pc.host,
                'port': pc.port,
                'token': pc.token
            }
            for name, pc in self.clients.items()
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_client(self, name, host, port, token):
        """Add a new client"""
        self.clients[name] = RemotePC(name, host, port, token)
        self.save_clients()
        print(f'✅ Cliente {name} agregado')

    def remove_client(self, name):
        """Remove a client"""
        if name in self.clients:
            del self.clients[name]
            self.save_clients()
            print(f'✅ Cliente {name} eliminado')
        else:
            print(f'❌ Cliente {name} no encontrado')

    def get_client(self, name):
        """Get a client by name"""
        return self.clients.get(name)

    def list_clients(self):
        """List all clients"""
        if not self.clients:
            print('No hay clientes configurados')
            return

        data = []
        for name, pc in self.clients.items():
            online = '🟢 Online' if pc.ping() else '🔴 Offline'
            data.append([name, pc.host, pc.port, online])

        headers = ['Nombre', 'Host', 'Puerto', 'Estado']
        print(tabulate(data, headers=headers, tablefmt='simple'))

def main():
    parser = argparse.ArgumentParser(description='Remote PC Control CLI')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Add client
    add_parser = subparsers.add_parser('add', help='Agregar PC remota')
    add_parser.add_argument('name', help='Nombre de la PC')
    add_parser.add_argument('host', help='Host/IP (Tailscale)')
    add_parser.add_argument('--port', type=int, default=9876, help='Puerto')
    add_parser.add_argument('--token', required=True, help='Token de autenticación')

    # Remove client
    remove_parser = subparsers.add_parser('remove', help='Eliminar PC remota')
    remove_parser.add_argument('name', help='Nombre de la PC')

    # List clients
    subparsers.add_parser('list', help='Listar PCs remotas')

    # Info
    info_parser = subparsers.add_parser('info', help='Información del sistema')
    info_parser.add_argument('name', help='Nombre de la PC')

    # Stats
    stats_parser = subparsers.add_parser('stats', help='Estadísticas en tiempo real')
    stats_parser.add_argument('name', help='Nombre de la PC')

    # Execute command
    exec_parser = subparsers.add_parser('exec', help='Ejecutar comando')
    exec_parser.add_argument('name', help='Nombre de la PC')
    exec_parser.add_argument('command', help='Comando a ejecutar')

    # Reboot
    reboot_parser = subparsers.add_parser('reboot', help='Reiniciar PC')
    reboot_parser.add_argument('name', help='Nombre de la PC')

    # Shutdown
    shutdown_parser = subparsers.add_parser('shutdown', help='Apagar PC')
    shutdown_parser.add_argument('name', help='Nombre de la PC')

    # Upload file
    upload_parser = subparsers.add_parser('upload', help='Subir archivo')
    upload_parser.add_argument('name', help='Nombre de la PC')
    upload_parser.add_argument('local', help='Archivo local')
    upload_parser.add_argument('remote', help='Ruta remota')

    # Download file
    download_parser = subparsers.add_parser('download', help='Descargar archivo')
    download_parser.add_argument('name', help='Nombre de la PC')
    download_parser.add_argument('remote', help='Archivo remoto')
    download_parser.add_argument('local', help='Ruta local')

    # Processes
    processes_parser = subparsers.add_parser('processes', help='Listar procesos')
    processes_parser.add_argument('name', help='Nombre de la PC')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = ControlManager()

    if args.command == 'add':
        manager.add_client(args.name, args.host, args.port, args.token)

    elif args.command == 'remove':
        manager.remove_client(args.name)

    elif args.command == 'list':
        manager.list_clients()

    elif args.command == 'info':
        pc = manager.get_client(args.name)
        if pc:
            info = pc.get_info()
            if info:
                for key, value in info.items():
                    print(f'{key}: {value}')

    elif args.command == 'stats':
        pc = manager.get_client(args.name)
        if pc:
            stats = pc.get_stats()
            if stats:
                print(f"CPU: {stats['cpu_percent_avg']:.1f}%")
                print(f"RAM: {stats['memory_percent']:.1f}% ({stats['memory_used'] / 1024**3:.1f} GB / {stats['memory_total'] / 1024**3:.1f} GB)")
                print(f"Disk: {stats['disk_percent']:.1f}% ({stats['disk_used'] / 1024**3:.1f} GB / {stats['disk_total'] / 1024**3:.1f} GB)")
                print(f"Network Sent: {stats['network_sent'] / 1024**2:.1f} MB")
                print(f"Network Recv: {stats['network_recv'] / 1024**2:.1f} MB")

    elif args.command == 'exec':
        pc = manager.get_client(args.name)
        if pc:
            result = pc.execute(args.command)
            if result:
                print(result['stdout'])
                if result['stderr']:
                    print(f"STDERR: {result['stderr']}", file=sys.stderr)
                print(f"Exit code: {result['returncode']}")

    elif args.command == 'reboot':
        pc = manager.get_client(args.name)
        if pc:
            confirm = input(f'¿Seguro que quieres reiniciar {args.name}? (s/N): ')
            if confirm.lower() == 's':
                result = pc.reboot()
                if result:
                    print(f"✅ {result['message']}")

    elif args.command == 'shutdown':
        pc = manager.get_client(args.name)
        if pc:
            confirm = input(f'¿Seguro que quieres apagar {args.name}? (s/N): ')
            if confirm.lower() == 's':
                result = pc.shutdown()
                if result:
                    print(f"✅ {result['message']}")

    elif args.command == 'upload':
        pc = manager.get_client(args.name)
        if pc:
            result = pc.upload_file(args.local, args.remote)
            if result:
                print(f"✅ {result['message']}")
                print(f"   Path: {result['path']}")
                print(f"   Size: {result['size']} bytes")

    elif args.command == 'download':
        pc = manager.get_client(args.name)
        if pc:
            if pc.download_file(args.remote, args.local):
                print(f"✅ Archivo descargado a {args.local}")

    elif args.command == 'processes':
        pc = manager.get_client(args.name)
        if pc:
            result = pc.get_processes()
            if result:
                data = [[p['pid'], p['name'], f"{p.get('cpu_percent', 0):.1f}%", f"{p.get('memory_percent', 0):.1f}%"]
                       for p in result['processes'][:20]]
                headers = ['PID', 'Name', 'CPU%', 'MEM%']
                print(tabulate(data, headers=headers, tablefmt='simple'))
                print(f"\nTotal processes: {result['total']}")

if __name__ == '__main__':
    main()
