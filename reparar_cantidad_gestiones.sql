-- Script para reparar inconsistencias en cantidad_gestiones
-- Ejecutar si el diagnóstico muestra inconsistencias

-- 1. Actualizar todos los registros con la cantidad correcta
UPDATE registro_base 
SET cantidad_gestiones = (
    SELECT COUNT(*) 
    FROM gestion g 
    WHERE g.registro_id = registro_base.id
);

-- 2. Verificar la reparación
WITH verificacion AS (
    SELECT 
        r.id,
        r.cantidad_gestiones as cantidad_stored,
        COUNT(g.id) as cantidad_real
    FROM registro_base r
    LEFT JOIN gestion g ON g.registro_id = r.id
    GROUP BY r.id, r.cantidad_gestiones
    HAVING r.cantidad_gestiones != COUNT(g.id)
)
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Todas las cantidades están correctas'
        ELSE CONCAT('❌ Aún hay ', COUNT(*), ' registros inconsistentes')
    END as resultado_reparacion
FROM verificacion;

-- 3. Mostrar estadísticas después de la reparación
SELECT 
    'Estadísticas después de reparación' as descripcion,
    COUNT(*) as total_registros,
    AVG(cantidad_gestiones)::NUMERIC(10,2) as promedio_gestiones,
    MAX(cantidad_gestiones) as max_gestiones,
    MIN(cantidad_gestiones) as min_gestiones
FROM registro_base;

RAISE NOTICE 'Reparación de cantidad_gestiones completada';
