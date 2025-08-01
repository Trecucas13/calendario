import psutil
import os
import time

# 1. Función de benchmarking
def benchmark_guardado(funcion, repeticiones=1):
    proceso = psutil.Process(os.getpid())
    memoria_inicial = proceso.memory_info().rss
    cpu_inicial = proceso.cpu_times()
    tiempo_inicial = time.time()

    for _ in range(repeticiones):
        funcion()
        print(f"repetición {_ + 1} de {repeticiones} ejecutada")

    tiempo_final = time.time()
    cpu_final = proceso.cpu_times()
    memoria_final = proceso.memory_info().rss

    print(f"\n🔁 Resultados de {repeticiones} ejecuciones:")
    print(f"⏱️ Tiempo total: {tiempo_final - tiempo_inicial:.4f} seg")
    print(f"⏱️ Tiempo promedio por inserción: {(tiempo_final - tiempo_inicial) / repeticiones:.6f} seg")
    print(f"🧠 Memoria usada total: {(memoria_final - memoria_inicial) / (1024**2):.2f} MB")
    print(f"🧠 Memoria promedio por ejecución: {((memoria_final - memoria_inicial) / repeticiones) / 1024:.2f} KB")
    print(f"🧮 CPU usuario: {cpu_final.user - cpu_inicial.user:.4f} seg")
    print(f"⚙️  CPU sistema: {cpu_final.system - cpu_inicial.system:.4f} seg")

# from models.vistas.gestiones import obtener_gestiones_bd


# 3. Ejecutas el benchmark
# benchmark_guardado(obtener_gestiones_bd, repeticiones=100)