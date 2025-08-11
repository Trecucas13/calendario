"""
Configuración de optimización de base de datos para queries con chunks
"""
import time
import logging
from functools import wraps

# Configurar logging para monitoreo de rendimiento
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_query_performance(func):
    """
    Decorador para medir y registrar el tiempo de ejecución de consultas
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log solo si la consulta toma más de 1 segundo
            if execution_time > 1.0:
                logger.warning(f"Consulta lenta detectada: {func.__name__} tomó {execution_time:.2f}s")
            else:
                logger.info(f"Query {func.__name__}: {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error en {func.__name__} después de {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

# Configuración de chunks optimizada según el uso
PERFORMANCE_CONFIG = {
    'gestiones': {
        'chunk_size': 1000,
        'max_records': 50000,
        'timeout_seconds': 30
    },
    'historico': {
        'chunk_size': 500,
        'max_records': 10000,
        'timeout_seconds': 15
    },
    'paginacion': {
        'per_page_default': 17,
        'per_page_max': 100,
        'cache_timeout': 300  # 5 minutos
    }
}

def get_optimized_chunk_size(query_type='gestiones'):
    """
    Obtiene el tamaño de chunk optimizado para el tipo de consulta
    """
    config = PERFORMANCE_CONFIG.get(query_type, PERFORMANCE_CONFIG['gestiones'])
    return config['chunk_size']

def get_max_records(query_type='gestiones'):
    """
    Obtiene el límite máximo de registros para el tipo de consulta
    """
    config = PERFORMANCE_CONFIG.get(query_type, PERFORMANCE_CONFIG['gestiones'])
    return config['max_records']
