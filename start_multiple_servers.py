"""
Start multiple instances of the Flask application on different ports.
This script allows running multiple backend instances simultaneously
on ports 5000-5005 for load balancing and high availability.
"""

import subprocess
import sys
import os
from pathlib import Path

def start_server(port, host='127.0.0.1'):
    """Start a Flask server instance on the specified port."""
    try:
        # Use the same app.py but with different port
        process = subprocess.Popen([
            sys.executable, 'app.py', 
            '--port', str(port), 
            '--host', host
        ], env={
            **os.environ,
            'FLASK_RUN_PORT': str(port),
            'FLASK_RUN_HOST': host
        })
        return process
    except Exception as e:
        print(f"Failed to start server on port {port}: {e}")
        return None

def main():
    """Main function to start multiple server instances."""
    ports = [5000, 5001, 5002, 5003, 5004, 5005]
    processes = []
    
    print("Starting multiple Flask instances...")
    
    for port in ports:
        print(f"Starting server on port {port}...")
        process = start_server(port)
        if process:
            processes.append((port, process))
    
    print(f"Started {len(processes)} server instances")
    print("Press Ctrl+C to stop all servers")
    
    try:
        # Keep the script running
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down all servers...")
        for port, process in processes:
            process.terminate()
            process.wait()
        print("All servers stopped")

if __name__ == '__main__':
    main()