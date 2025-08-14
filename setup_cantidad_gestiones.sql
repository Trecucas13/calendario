-- Script para crear la columna cantidad_gestiones y trigger automático
-- Ejecutar este script una sola vez en la base de datos

-- 1. Agregar la columna cantidad_gestiones si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'registro_base' 
        AND column_name = 'cantidad_gestiones'
    ) THEN
        ALTER TABLE registro_base ADD COLUMN cantidad_gestiones INTEGER DEFAULT 0;
        
        -- Inicializar los valores existentes
        UPDATE registro_base 
        SET cantidad_gestiones = (
            SELECT COUNT(*) 
            FROM gestion g 
            WHERE g.registro_id = registro_base.id
        );
        
        RAISE NOTICE 'Columna cantidad_gestiones creada e inicializada';
    ELSE
        RAISE NOTICE 'La columna cantidad_gestiones ya existe';
    END IF;
END $$;

-- 2. Crear función para actualizar automáticamente el contador
CREATE OR REPLACE FUNCTION actualizar_cantidad_gestiones()
RETURNS TRIGGER AS $$
BEGIN
    -- Debug: Registrar en log qué operación se está ejecutando
    RAISE NOTICE 'Trigger ejecutado: operación = %, registro_id = %', TG_OP, COALESCE(NEW.registro_id, OLD.registro_id);
    
    IF TG_OP = 'DELETE' THEN
        -- Cuando se elimina una gestión
        UPDATE registro_base 
        SET cantidad_gestiones = GREATEST(cantidad_gestiones - 1, 0)
        WHERE id = OLD.registro_id;
        
        RAISE NOTICE 'Gestión eliminada para registro_id = %, nueva cantidad = %', 
                     OLD.registro_id, 
                     (SELECT cantidad_gestiones FROM registro_base WHERE id = OLD.registro_id);
        RETURN OLD;
        
    ELSIF TG_OP = 'INSERT' THEN
        -- Cuando se inserta una gestión
        UPDATE registro_base 
        SET cantidad_gestiones = COALESCE(cantidad_gestiones, 0) + 1 
        WHERE id = NEW.registro_id;
        
        RAISE NOTICE 'Gestión insertada para registro_id = %, nueva cantidad = %', 
                     NEW.registro_id, 
                     (SELECT cantidad_gestiones FROM registro_base WHERE id = NEW.registro_id);
        RETURN NEW;
        
    ELSIF TG_OP = 'UPDATE' THEN
        -- Si cambia el registro_id de una gestión (poco probable pero posible)
        IF OLD.registro_id != NEW.registro_id THEN
            -- Decrementar el registro anterior
            UPDATE registro_base 
            SET cantidad_gestiones = GREATEST(cantidad_gestiones - 1, 0)
            WHERE id = OLD.registro_id;
            
            -- Incrementar el registro nuevo
            UPDATE registro_base 
            SET cantidad_gestiones = COALESCE(cantidad_gestiones, 0) + 1 
            WHERE id = NEW.registro_id;
            
            RAISE NOTICE 'Gestión movida de registro_id = % a registro_id = %', OLD.registro_id, NEW.registro_id;
        END IF;
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 3. Crear el trigger (con soporte para INSERT, UPDATE y DELETE)
DROP TRIGGER IF EXISTS trigger_cantidad_gestiones ON gestion;
CREATE TRIGGER trigger_cantidad_gestiones
    AFTER INSERT OR UPDATE OR DELETE ON gestion
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_cantidad_gestiones();

-- Verificar que el trigger se creó correctamente
SELECT 
    trigger_name,
    event_manipulation,
    action_timing,
    action_statement
FROM information_schema.triggers 
WHERE trigger_name = 'trigger_cantidad_gestiones';

-- 4. Verificar la configuración y hacer un test
SELECT 
    'Configuración completada' as estado,
    COUNT(*) as total_registros,
    AVG(cantidad_gestiones)::NUMERIC(10,2) as promedio_gestiones,
    MAX(cantidad_gestiones) as max_gestiones
FROM registro_base;

-- 5. Test del trigger - Insertar y eliminar una gestión de prueba
DO $$
DECLARE
    test_registro_id INTEGER;
    cantidad_antes INTEGER;
    cantidad_despues INTEGER;
BEGIN
    -- Seleccionar un registro existente para hacer la prueba
    SELECT id INTO test_registro_id 
    FROM registro_base 
    LIMIT 1;
    
    IF test_registro_id IS NOT NULL THEN
        -- Obtener cantidad antes
        SELECT cantidad_gestiones INTO cantidad_antes 
        FROM registro_base 
        WHERE id = test_registro_id;
        
        RAISE NOTICE 'Test iniciado - registro_id: %, cantidad antes: %', test_registro_id, cantidad_antes;
        
        -- Insertar gestión de prueba
        INSERT INTO gestion (registro_id, tipificacion, comentario, usuario, llave_compuesta)
        VALUES (test_registro_id, 'TEST_TRIGGER', 'Prueba de trigger', 'SYSTEM', 'TEST-TRIGGER-001');
        
        -- Obtener cantidad después de insertar
        SELECT cantidad_gestiones INTO cantidad_despues 
        FROM registro_base 
        WHERE id = test_registro_id;
        
        RAISE NOTICE 'Después de INSERT - cantidad: %', cantidad_despues;
        
        -- Eliminar gestión de prueba
        DELETE FROM gestion 
        WHERE registro_id = test_registro_id 
        AND tipificacion = 'TEST_TRIGGER' 
        AND comentario = 'Prueba de trigger';
        
        -- Obtener cantidad final
        SELECT cantidad_gestiones INTO cantidad_despues 
        FROM registro_base 
        WHERE id = test_registro_id;
        
        RAISE NOTICE 'Después de DELETE - cantidad: %', cantidad_despues;
        
        IF cantidad_despues = cantidad_antes THEN
            RAISE NOTICE 'TEST EXITOSO: El trigger funciona correctamente';
        ELSE
            RAISE NOTICE 'TEST FALLIDO: Cantidad esperada: %, cantidad actual: %', cantidad_antes, cantidad_despues;
        END IF;
    ELSE
        RAISE NOTICE 'No se encontraron registros para hacer el test';
    END IF;
END $$;
