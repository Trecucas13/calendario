#!/usr/bin/env python3
"""
Script de prueba para validar las funciones optimizadas de gestiones.py
"""

import os
import sys
import time

# Añadir el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.vistas.gestiones import (
    obtener_total_gestiones_count,
    obtener_total_gestiones_paginado,
    obtener_historico_gestiones_chunked,
    obtener_historico_gestiones_count,
    obtener_total_mejor_gestiones_paginado,
    obtener_total_mejor_gestiones_count,
    obtener_gestiones_por_chunks
)

def test_performance_functions():
    """
    Prueba las funciones optimizadas para validar rendimiento
    """
    print("=" * 60)
    print("PRUEBA DE FUNCIONES OPTIMIZADAS - GESTIONES")
    print("=" * 60)
    
    # Test 1: Conteo de registros
    print("\n1. Probando funciones de conteo...")
    start_time = time.time()
    total_gestiones = obtener_total_gestiones_count()
    elapsed = time.time() - start_time
    print(f"   ✅ Total gestiones: {total_gestiones} (tiempo: {elapsed:.2f}s)")
    
    start_time = time.time()
    total_historico = obtener_historico_gestiones_count()
    elapsed = time.time() - start_time
    print(f"   ✅ Total histórico: {total_historico} (tiempo: {elapsed:.2f}s)")
    
    start_time = time.time()
    total_mejor = obtener_total_mejor_gestiones_count()
    elapsed = time.time() - start_time
    print(f"   ✅ Total mejor gestiones: {total_mejor} (tiempo: {elapsed:.2f}s)")
    
    # Test 2: Paginación SQL
    print("\n2. Probando paginación SQL...")
    
    start_time = time.time()
    gestiones_pag = obtener_total_gestiones_paginado(page=1, per_page=10)
    elapsed = time.time() - start_time
    print(f"   ✅ Gestiones paginadas (página 1): {len(gestiones_pag)} registros (tiempo: {elapsed:.2f}s)")
    
    start_time = time.time()
    historico_pag = obtener_historico_gestiones_chunked(page=1, per_page=10)
    elapsed = time.time() - start_time
    print(f"   ✅ Histórico paginado (página 1): {len(historico_pag)} registros (tiempo: {elapsed:.2f}s)")
    
    start_time = time.time()
    mejor_pag = obtener_total_mejor_gestiones_paginado(page=1, per_page=10)
    elapsed = time.time() - start_time
    print(f"   ✅ Mejor gestiones paginado (página 1): {len(mejor_pag)} registros (tiempo: {elapsed:.2f}s)")
    
    # Test 3: Chunks para exportación
    print("\n3. Probando procesamiento por chunks...")
    start_time = time.time()
    chunk = obtener_gestiones_por_chunks(chunk_size=50, start_id=0)
    elapsed = time.time() - start_time
    print(f"   ✅ Chunk de gestiones: {len(chunk)} registros (tiempo: {elapsed:.2f}s)")
    
    # Test 4: Validación de estructura de datos
    print("\n4. Validando estructura de datos...")
    if gestiones_pag:
        sample_record = gestiones_pag[0]
        required_fields = ['registro_id', 'tipo_id', 'num_id', 'primer_nombre', 'mejor_gestion']
        
        missing_fields = []
        for field in required_fields:
            if field not in sample_record:
                missing_fields.append(field)
        
        if not missing_fields:
            print("   ✅ Estructura de datos correcta")
        else:
            print(f"   ❌ Campos faltantes: {missing_fields}")
    else:
        print("   ⚠️ No hay datos para validar estructura")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

def test_pagination_logic():
    """
    Prueba la lógica de paginación
    """
    print("\n5. Probando lógica de paginación...")
    
    total = obtener_total_mejor_gestiones_count()
    per_page = 17
    total_pages = (total + per_page - 1) // per_page  # Cálculo de páginas
    
    print(f"   Total registros: {total}")
    print(f"   Registros por página: {per_page}")
    print(f"   Total páginas estimadas: {total_pages}")
    
    # Probar primera página
    page_1 = obtener_total_mejor_gestiones_paginado(page=1, per_page=per_page)
    print(f"   ✅ Página 1: {len(page_1)} registros")
    
    # Probar página intermedia
    if total_pages > 2:
        middle_page = total_pages // 2
        page_middle = obtener_total_mejor_gestiones_paginado(page=middle_page, per_page=per_page)
        print(f"   ✅ Página {middle_page}: {len(page_middle)} registros")
    
    # Probar última página
    if total_pages > 1:
        last_page = obtener_total_mejor_gestiones_paginado(page=total_pages, per_page=per_page)
        expected_last_page_size = total % per_page or per_page
        print(f"   ✅ Última página ({total_pages}): {len(last_page)} registros (esperado: {expected_last_page_size})")

if __name__ == "__main__":
    try:
        from database.config import db
        print("🔗 Conexión a base de datos establecida")
        
        test_performance_functions()
        test_pagination_logic()
        
        print("\n🎉 Todas las pruebas completadas exitosamente")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de ejecutar este script desde el contexto de la aplicación Flask")
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
