#!/usr/bin/env python3
"""
Remote PC Control Agent
Runs on remote PCs to receive and execute commands
"""

import os
import sys
import json
import time
import socket
import platform
import subprocess
import threading
import psutil
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
import logging

# Configuration
CONFIG_FILE = Path.home() / '.remote-pc-agent' / 'config.json'
LOG_FILE = Path.home() / '.remote-pc-agent' / 'agent.log'
TOKEN_FILE = Path.home() / '.remote-pc-agent' / 'token'

# Setup logging
os.makedirs(CONFIG_FILE.parent, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class AgentConfig:
    def __init__(self):
        self.port = 9876
        self.server_token = None
        self.pc_name = socket.gethostname()
        self.load_config()

    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                self.port = config.get('port', self.port)
                self.server_token = config.get('server_token')
                self.pc_name = config.get('pc_name', self.pc_name)

        if TOKEN_FILE.exists():
            with open(TOKEN_FILE) as f:
                self.server_token = f.read().strip()

    def save_config(self):
        config = {
            'port': self.port,
            'pc_name': self.pc_name
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        if self.server_token:
            with open(TOKEN_FILE, 'w') as f:
                f.write(self.server_token)
            os.chmod(TOKEN_FILE, 0o600)

config = AgentConfig()

def verify_token():
    """Verify authentication token"""
    token = request.headers.get('Authorization')
    if not token or not config.server_token:
        return False
    return token == f'Bearer {config.server_token}'

def require_auth(f):
    """Decorator to require authentication"""
    def decorated(*args, **kwargs):
        if not verify_token():
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route('/ping', methods=['GET'])
def ping():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'pc_name': config.pc_name,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/info', methods=['GET'])
@require_auth
def get_info():
    """Get system information"""
    try:
        return jsonify({
            'pc_name': config.pc_name,
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        })
    except Exception as e:
        logger.error(f'Error getting info: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get real-time system stats"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()

        return jsonify({
            'cpu_percent': cpu_percent,
            'cpu_percent_avg': sum(cpu_percent) / len(cpu_percent),
            'memory_percent': memory.percent,
            'memory_used': memory.used,
            'memory_total': memory.total,
            'disk_percent': disk.percent,
            'disk_used': disk.used,
            'disk_total': disk.total,
            'network_sent': net.bytes_sent,
            'network_recv': net.bytes_recv,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f'Error getting stats: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/execute', methods=['POST'])
@require_auth
def execute_command():
    """Execute a command"""
    try:
        data = request.get_json()
        command = data.get('command')
        shell = data.get('shell', True)
        timeout = data.get('timeout', 300)

        if not command:
            return jsonify({'error': 'No command provided'}), 400

        logger.info(f'Executing command: {command}')

        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return jsonify({
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timeout'}), 408
    except Exception as e:
        logger.error(f'Error executing command: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/reboot', methods=['POST'])
@require_auth
def reboot_system():
    """Reboot the system"""
    try:
        logger.warning('Reboot requested')

        def do_reboot():
            time.sleep(2)
            if platform.system() == 'Windows':
                os.system('shutdown /r /t 5')
            else:
                os.system('sudo shutdown -r +1')

        thread = threading.Thread(target=do_reboot)
        thread.daemon = True
        thread.start()

        return jsonify({
            'message': 'Reboot scheduled',
            'platform': platform.system()
        })
    except Exception as e:
        logger.error(f'Error rebooting: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/shutdown', methods=['POST'])
@require_auth
def shutdown_system():
    """Shutdown the system"""
    try:
        logger.warning('Shutdown requested')

        def do_shutdown():
            time.sleep(2)
            if platform.system() == 'Windows':
                os.system('shutdown /s /t 5')
            else:
                os.system('sudo shutdown -h +1')

        thread = threading.Thread(target=do_shutdown)
        thread.daemon = True
        thread.start()

        return jsonify({
            'message': 'Shutdown scheduled',
            'platform': platform.system()
        })
    except Exception as e:
        logger.error(f'Error shutting down: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    """Receive a file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        dest_path = request.form.get('path')

        if not dest_path:
            return jsonify({'error': 'No destination path provided'}), 400

        dest_path = Path(dest_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        file.save(dest_path)
        logger.info(f'File uploaded to {dest_path}')

        return jsonify({
            'message': 'File uploaded successfully',
            'path': str(dest_path),
            'size': dest_path.stat().st_size
        })
    except Exception as e:
        logger.error(f'Error uploading file: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['GET'])
@require_auth
def download_file():
    """Download a file"""
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400

        file_path = Path(file_path)
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        logger.info(f'File downloaded from {file_path}')
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f'Error downloading file: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/processes', methods=['GET'])
@require_auth
def get_processes():
    """Get list of running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)

        return jsonify({
            'processes': processes[:50],  # Top 50
            'total': len(processes)
        })
    except Exception as e:
        logger.error(f'Error getting processes: {e}')
        return jsonify({'error': str(e)}), 500

def main():
    logger.info(f'Starting Remote PC Agent on {config.pc_name}')
    logger.info(f'Listening on port {config.port}')

    if not config.server_token:
        logger.warning('No authentication token set! Run setup_agent.py first.')

    app.run(host='0.0.0.0', port=config.port, debug=False)

if __name__ == '__main__':
    main()
