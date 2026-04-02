#!/usr/bin/env python3
"""
Remote PC Control Web Server
Web dashboard to monitor and control remote PCs
"""

import json
import asyncio
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from control import ControlManager

app = Flask(__name__)
manager = ControlManager()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/clients')
def api_clients():
    """Get all clients and their status"""
    clients_data = []
    for name, pc in manager.clients.items():
        online = pc.ping()
        client_info = {
            'name': name,
            'host': pc.host,
            'port': pc.port,
            'online': online
        }

        if online:
            info = pc.get_info()
            stats = pc.get_stats()
            if info:
                client_info.update(info)
            if stats:
                client_info['stats'] = stats

        clients_data.append(client_info)

    return jsonify(clients_data)

@app.route('/api/client/<name>/stats')
def api_client_stats(name):
    """Get real-time stats for a specific client"""
    pc = manager.get_client(name)
    if not pc:
        return jsonify({'error': 'Client not found'}), 404

    stats = pc.get_stats()
    if stats:
        return jsonify(stats)
    else:
        return jsonify({'error': 'Could not get stats'}), 500

@app.route('/api/client/<name>/execute', methods=['POST'])
def api_client_execute(name):
    """Execute command on a specific client"""
    pc = manager.get_client(name)
    if not pc:
        return jsonify({'error': 'Client not found'}), 404

    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({'error': 'No command provided'}), 400

    result = pc.execute(command)
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Could not execute command'}), 500

@app.route('/api/client/<name>/reboot', methods=['POST'])
def api_client_reboot(name):
    """Reboot a specific client"""
    pc = manager.get_client(name)
    if not pc:
        return jsonify({'error': 'Client not found'}), 404

    result = pc.reboot()
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Could not reboot'}), 500

@app.route('/api/client/<name>/shutdown', methods=['POST'])
def api_client_shutdown(name):
    """Shutdown a specific client"""
    pc = manager.get_client(name)
    if not pc:
        return jsonify({'error': 'Client not found'}), 404

    result = pc.shutdown()
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Could not shutdown'}), 500

@app.route('/api/client/<name>/processes')
def api_client_processes(name):
    """Get processes for a specific client"""
    pc = manager.get_client(name)
    if not pc:
        return jsonify({'error': 'Client not found'}), 404

    result = pc.get_processes()
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Could not get processes'}), 500

def main():
    print("="*50)
    print("Remote PC Control - Web Dashboard")
    print("="*50)
    print("\n🌐 Server starting at http://localhost:8080")
    print("   Open this URL in your browser\n")
    print(f"📊 Monitoring {len(manager.clients)} PC(s)")
    for name in manager.clients.keys():
        print(f"   - {name}")
    print("\nPress Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    main()
