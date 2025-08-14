-- Script de diagnóstico para verificar el estado de cantidad_gestiones
-- Ejecutar este script para verificar si el trigger está funcionando

-- 1. Verificar si la columna existe
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'registro_base' 
            AND column_name = 'cantidad_gestiones'
        ) 
        THEN '✅ La columna cantidad_gestiones EXISTE'
        ELSE '❌ La columna cantidad_gestiones NO EXISTE'
    END as estado_columna;

-- 2. Verificar si el trigger existe
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.triggers 
            WHERE trigger_name = 'trigger_cantidad_gestiones'
        ) 
        THEN '✅ El trigger trigger_cantidad_gestiones EXISTE'
        ELSE '❌ El trigger trigger_cantidad_gestiones NO EXISTE'
    END as estado_trigger;

-- 3. Verificar si la función existe
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.routines 
            WHERE routine_name = 'actualizar_cantidad_gestiones'
        ) 
        THEN '✅ La función actualizar_cantidad_gestiones EXISTE'
        ELSE '❌ La función actualizar_cantidad_gestiones NO EXISTE'
    END as estado_funcion;

-- 4. Mostrar estadísticas actuales
SELECT 
    'Estadísticas actuales' as descripcion,
    COUNT(*) as total_registros,
    COUNT(cantidad_gestiones) as registros_con_cantidad,
    AVG(cantidad_gestiones)::NUMERIC(10,2) as promedio_gestiones,
    MAX(cantidad_gestiones) as max_gestiones,
    MIN(cantidad_gestiones) as min_gestiones
FROM registro_base;

-- 5. Mostrar registros con inconsistencias (donde cantidad_gestiones no coincide)
SELECT 
    r.id,
    r.cantidad_gestiones as cantidad_stored,
    COUNT(g.id) as cantidad_real,
    (r.cantidad_gestiones - COUNT(g.id)) as diferencia
FROM registro_base r
LEFT JOIN gestion g ON g.registro_id = r.id
GROUP BY r.id, r.cantidad_gestiones
HAVING r.cantidad_gestiones IS NULL OR r.cantidad_gestiones != COUNT(g.id)
ORDER BY diferencia DESC
LIMIT 10;

-- 6. Contar total de inconsistencias
WITH inconsistencias AS (
    SELECT 
        r.id,
        r.cantidad_gestiones as cantidad_stored,
        COUNT(g.id) as cantidad_real
    FROM registro_base r
    LEFT JOIN gestion g ON g.registro_id = r.id
    GROUP BY r.id, r.cantidad_gestiones
    HAVING r.cantidad_gestiones IS NULL OR r.cantidad_gestiones != COUNT(g.id)
)
SELECT 
    COUNT(*) as registros_inconsistentes,
    (SELECT COUNT(*) FROM registro_base) as total_registros,
    ROUND((COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM registro_base)) * 100, 2) as porcentaje_inconsistente
FROM inconsistencias;
