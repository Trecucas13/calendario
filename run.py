import subprocess
import sys
import time 

flask_process = [
    "python",
    "app.py",
]

flask_cwd = "."


fastapi_process = [
    "uvicorn",
    "app.main:app",
    "--reload", 
]

fastapi_cwd = "./backend"

def run_process(command, cwd):
    """Ejecuta un comando en un subproceso"""
    return subprocess.Popen(
        command, cwd=cwd, stdout=sys.stdout, stderr=sys.stderr, shell=True
    )


if __name__ == "__main__":
    try:
        # Iniciar backend
        print("🚀 Iniciando servidor flask...")
        backend_process = run_process(flask_process, flask_cwd)

        # Pequeña pausa para permitir que el backend se inicialice primero
        time.sleep(25)

        # Iniciar frontend
        print("💅 Iniciando servidor fastapi...")
        frontend_process = run_process(fastapi_process, fastapi_cwd)

        # Mantener el script activo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🔴 Deteniendo servidores...")
        # Verificar si los procesos existen antes de intentar terminarlos
        if "backend_process" in locals():
            backend_process.terminate()
            backend_process.wait()

        if "frontend_process" in locals():
            frontend_process.terminate()
            frontend_process.wait()

        print("✅ Servidores detenidos correctamente")