from flask import Blueprint, render_template, flash, request
import math
from database.config import db
from auth.decorators import *
from auth.decorators import login_required, role_required
from sqlalchemy import text
from datetime import datetime

vista_gestiones = Blueprint('vista_gestiones', __name__)

def try_parse_date(date_string):
    formats = [
        '%Y-%m-%d %H:%M:%S',  # Current format
        '%Y-%m-%dT%H:%M:%S'   # ISO format
    ]
    for date_format in formats:
        try:
            return datetime.strptime(date_string, date_format)
        except Exception:
            continue
    return None

# ===================== CONSULTAS ENRIQUECIDAS =====================
def obtener_historico_gestiones():
    sql = text("""
        SELECT 
            g.id AS gestion_id,
            g.tipificacion,
            g.comentario,
            g.id_llamada,
            -- Convert to Colombia timezone and format date
            TO_CHAR((g.fecha_gestion AT TIME ZONE 'UTC') AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD HH24:MI:SS') AS fecha_gestion,
            g.usuario AS asesor,
            g.registro_id,
            g.llave_compuesta,
            g.motivo as motivo,
            r.id AS registro_id,
            r.tipo_id,
            r.num_id,
            r.primer_nombre,
            r.segundo_nombre,
            r.primer_apellido,
            r.segundo_apellido,
            r.fecha,
            r.edad,
            r.estado_afiliacion,
            r.regimen_afiliacion,
            r.telefonos,
            r.direccion,
            r.municipio,
            r.subregion,
            r.proceso,
            r.fecha_carga,
            -- Mejor gestión (por menor ranking)
            COALESCE(
                (
                    SELECT g2.tipificacion
                    FROM gestion g2
                    JOIN tipificacion t2 ON t2.nombre = g2.tipificacion
                    WHERE g2.registro_id = r.id
                    ORDER BY t2.ranking ASC
                    LIMIT 1
                ),
                'Sin gestión'
            ) AS mejor_gestion,
            -- Mes de la última gestión
            (
                SELECT TO_CHAR((g3.fecha_gestion AT TIME ZONE 'UTC') AT TIME ZONE 'America/Bogota', 'Month')
                FROM gestion g3
                WHERE g3.registro_id = r.id
                ORDER BY g3.fecha_gestion DESC
                LIMIT 1
            ) AS mes,
            -- Cantidad de gestiones
            (
                SELECT COUNT(*)
                FROM gestion g4
                WHERE g4.registro_id = r.id
            ) AS cantidad_gestiones,
            -- Tipo de gestión (efectivo/no efectivo)
            (
                SELECT CASE WHEN t3.tipo_contacto = 'efectivo' THEN 'efectivo' ELSE 'no efectivo' END
                FROM gestion g5
                JOIN tipificacion t3 ON t3.nombre = g5.tipificacion
                WHERE g5.registro_id = r.id
                ORDER BY g5.fecha_gestion DESC
                LIMIT 1
            ) AS tipo_gestion
        FROM gestion g
        JOIN registro_base r ON r.id = g.registro_id
        ORDER BY g.fecha_gestion DESC
    """)
    result = db.session.execute(sql).mappings().all()
    print(result)
    return result

def obtener_total_gestiones():
    sql = text("""
        SELECT 
            r.id AS registro_id,
            r.tipo_id,
            r.num_id,
            r.primer_nombre,
            r.segundo_nombre,
            r.primer_apellido,
            r.segundo_apellido,
            r.fecha,
            r.edad,
            r.estado_afiliacion,
            r.regimen_afiliacion,
            r.proceso,
            r.telefonos,
            r.direccion,
            r.municipio,
            r.subregion,
            r.fecha_carga,
            g.motivo as motivo,
            -- Mejor gestión (por menor ranking)
            COALESCE(
                (
                    SELECT g2.tipificacion
                    FROM gestion g2
                    JOIN tipificacion t2 ON t2.nombre = g2.tipificacion
                    WHERE g2.registro_id = r.id
                    ORDER BY t2.ranking ASC
                    LIMIT 1
                ),
                'Sin gestión'
            ) AS mejor_gestion,
            -- Última gestión
            (
                SELECT g3.tipificacion
                FROM gestion g3
                WHERE g3.registro_id = r.id
                ORDER BY g3.fecha_gestion DESC
                LIMIT 1
            ) AS tipificacion,
            (
                SELECT t3.tipo_contacto
                FROM gestion g4
                JOIN tipificacion t3 ON t3.nombre = g4.tipificacion
                WHERE g4.registro_id = r.id
                ORDER BY g4.fecha_gestion DESC
                LIMIT 1
            ) AS tipo_contacto,
            (
                SELECT g5.comentario
                FROM gestion g5
                WHERE g5.registro_id = r.id
                ORDER BY g5.fecha_gestion DESC
                LIMIT 1
            ) AS comentario,
            (
                SELECT g6.id_llamada
                FROM gestion g6
                WHERE g6.registro_id = r.id
                ORDER BY g6.fecha_gestion DESC
                LIMIT 1
            ) AS id_llamada,
            (
                SELECT TO_CHAR((g7.fecha_gestion AT TIME ZONE 'UTC') AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD HH24:MI:SS')
                FROM gestion g7
                WHERE g7.registro_id = r.id
                ORDER BY g7.fecha_gestion DESC
                LIMIT 1
            ) AS fecha_gestion,
            (
                SELECT g8.usuario
                FROM gestion g8
                WHERE g8.registro_id = r.id
                ORDER BY g8.fecha_gestion DESC
                LIMIT 1
            ) AS asesor,
            (
                SELECT CASE WHEN t4.tipo_contacto = 'efectivo' THEN 'efectivo' ELSE 'no efectivo' END
                FROM gestion g9
                JOIN tipificacion t4 ON t4.nombre = g9.tipificacion
                WHERE g9.registro_id = r.id
                ORDER BY g9.fecha_gestion DESC
                LIMIT 1
            ) AS tipo_gestion,
            (
                SELECT TO_CHAR((g10.fecha_gestion AT TIME ZONE 'UTC') AT TIME ZONE 'America/Bogota', 'Month')
                FROM gestion g10
                WHERE g10.registro_id = r.id
                ORDER BY g10.fecha_gestion DESC
                LIMIT 1
            ) AS mes,
            (
                SELECT COUNT(*)
                FROM gestion g11
                WHERE g11.registro_id = r.id
            ) AS cantidad_gestiones
        FROM registro_base r
        LEFT JOIN gestion g ON g.registro_id = r.id
        ORDER BY r.fecha_carga DESC
    """)
    result = db.session.execute(sql).mappings().all()
    return result

def obtener_tipificaciones():
    sql = text("""
        SELECT id, nombre, ranking, tipo_contacto
        FROM tipificacion
        ORDER BY ranking ASC
    """)
    result = db.session.execute(sql).mappings().all()
    return result

def obtener_gestiones_bd():
    sql = text("""
        SELECT 
            g.id AS gestion_id,
            g.tipificacion,
            g.comentario,
            g.id_llamada,
            g.fecha_gestion,
            g.usuario AS asesor,
            g.registro_id,
            g.llave_compuesta,
            g.motivo,
            r.tipo_id,
            r.num_id,
            r.primer_nombre,
            r.segundo_nombre,
            r.primer_apellido,
            r.segundo_apellido,
            r.fecha,
            r.edad,
            r.estado_afiliacion,
            r.regimen_afiliacion,
            r.telefonos,
            r.direccion,
            r.municipio,
            r.subregion,
            r.proceso,
            r.fecha_carga,
            -- Mejor gestión (por menor ranking)
            COALESCE(
                (
                    SELECT g2.tipificacion
                    FROM gestion g2
                    JOIN tipificacion t2 ON t2.nombre = g2.tipificacion
                    WHERE g2.registro_id = r.id
                    ORDER BY t2.ranking ASC
                    LIMIT 1
                ),
                'Sin gestión'
            ) AS mejor_gestion,
            -- Mes de la última gestión
            (
                SELECT TO_CHAR((g3.fecha_gestion AT TIME ZONE 'UTC') AT TIME ZONE 'America/Bogota', 'Month')
                FROM gestion g3
                WHERE g3.registro_id = r.id
                ORDER BY g3.fecha_gestion DESC
                LIMIT 1
            ) AS mes,
            -- Cantidad de gestiones
            (
                SELECT COUNT(*)
                FROM gestion g4
                WHERE g4.registro_id = r.id
            ) AS cantidad_gestiones,
            -- Tipo de gestión (efectivo/no efectivo)
            (
                SELECT CASE WHEN t3.tipo_contacto = 'efectivo' THEN 'efectivo' ELSE 'no efectivo' END
                FROM gestion g5
                JOIN tipificacion t3 ON t3.nombre = g5.tipificacion
                WHERE g5.registro_id = r.id
                ORDER BY g5.fecha_gestion DESC
                LIMIT 1
            ) AS tipo_gestion
        FROM gestion g
        JOIN registro_base r ON r.id = g.registro_id
        ORDER BY g.fecha_gestion DESC
    """)
    result = db.session.execute(sql).mappings().all()
    return result

def obtener_total_mejor_gestiones():
    sql = text("""
        SELECT
            r.id AS registro_id,
            r.tipo_id,
            r.num_id,
            r.primer_nombre,
            r.segundo_nombre,
            r.primer_apellido,
            r.segundo_apellido,
            r.fecha,
            r.edad,
            r.estado_afiliacion,
            r.regimen_afiliacion,
            r.proceso,
            r.telefonos,
            r.direccion,
            r.municipio,
            r.subregion,
            r.fecha_carga,
            -- Mejor gestión (por menor ranking)
            COALESCE(
                (
                    SELECT g2.tipificacion
                    FROM gestion g2
                    JOIN tipificacion t2 ON t2.nombre = g2.tipificacion
                    WHERE g2.registro_id = r.id
                    ORDER BY t2.ranking ASC
                    LIMIT 1
                ),
                'Sin gestión'
            ) AS mejor_gestion,
            -- Última gestión
            (
                SELECT g3.tipificacion
                FROM gestion g3
                WHERE g3.registro_id = r.id
                ORDER BY g3.fecha_gestion DESC
                LIMIT 1
            ) AS tipificacion,
            (
                SELECT t3.tipo_contacto
                FROM gestion g4
                JOIN tipificacion t3 ON t3.nombre = g4.tipificacion
                WHERE g4.registro_id = r.id
                ORDER BY g4.fecha_gestion DESC
                LIMIT 1
            ) AS tipo_contacto,
            (
                SELECT g5.comentario
                FROM gestion g5
                WHERE g5.registro_id = r.id
                ORDER BY g5.fecha_gestion DESC
                LIMIT 1
            ) AS comentario,
            (
                SELECT g6.id_llamada
                FROM gestion g6
                WHERE g6.registro_id = r.id
                ORDER BY g6.fecha_gestion DESC
                LIMIT 1
            ) AS id_llamada,
            (
                SELECT TO_CHAR((g7.fecha_gestion AT TIME ZONE 'UTC') AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD HH24:MI:SS')
                FROM gestion g7
                WHERE g7.registro_id = r.id
                ORDER BY g7.fecha_gestion DESC
                LIMIT 1
            ) AS fecha_gestion,
            (
                SELECT g8.usuario
                FROM gestion g8
                WHERE g8.registro_id = r.id
                ORDER BY g8.fecha_gestion DESC
                LIMIT 1
            ) AS asesor,
            (
                SELECT CASE WHEN t4.tipo_contacto = 'efectivo' THEN 'efectivo' ELSE 'no efectivo' END
                FROM gestion g9
                JOIN tipificacion t4 ON t4.nombre = g9.tipificacion
                WHERE g9.registro_id = r.id
                ORDER BY g9.fecha_gestion DESC
                LIMIT 1
            ) AS tipo_gestion,
            (
                SELECT TO_CHAR((g10.fecha_gestion AT TIME ZONE 'UTC') AT TIME ZONE 'America/Bogota', 'Month')
                FROM gestion g10
                WHERE g10.registro_id = r.id
                ORDER BY g10.fecha_gestion DESC
                LIMIT 1
            ) AS mes,
            (
                SELECT COUNT(*)
                FROM gestion g11
                WHERE g11.registro_id = r.id
            ) AS cantidad_gestiones
        FROM registro_base r
        ORDER BY r.fecha_carga DESC
    """)
    result = db.session.execute(sql).mappings().all()
    return result


# ================== RUTAS ==================
# Clase de paginación igual que antes
class Pagination:
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = math.ceil(total / per_page)
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None
    def iter_pages(self):
        return range(1, self.pages + 1)

@vista_gestiones.route("/Historico_gestiones")
@login_required
@role_required([1 , 2])
def tabla_gestiones():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    historial = obtener_historico_gestiones()
    tipificaciones = obtener_tipificaciones()
    total = len(historial)
    # Pagina en Python
    historial_paginado = historial[(page-1)*per_page : page*per_page]
    pagination = Pagination(page, per_page, total)
    return render_template("historico_gestiones.html", historico=historial_paginado, tipificaciones=tipificaciones, pagination=pagination)

#Ruta para Gestion BD
gestion_bd = Blueprint('gestion_bd', __name__)

@gestion_bd.route("/gestion_bd")
@login_required
@role_required([1 , 2])
def tabla_gestiones_bd():
    page = request.args.get('page', 1, type=int)
    per_page = 17
    historial = obtener_total_mejor_gestiones()
    total = len(historial)
    historial_paginado = historial[(page-1)*per_page : page*per_page]
    pagination = Pagination(page, per_page, total)
    return render_template("gestion_bd.html", historico=historial_paginado, pagination=pagination)

#Ruta para Gestionar
gestionar = Blueprint('gestionar', __name__)

@gestionar.route("/gestionar")
@login_required
@role_required([1 , 2])
def tabla_gestionar():
    page = request.args.get('page', 1, type=int)
    per_page = 17
    gestiones = obtener_total_gestiones()
    tipificaciones = obtener_tipificaciones()
    total = len(gestiones)
    gestiones_paginado = gestiones[(page-1)*per_page : page*per_page]
    pagination = Pagination(page, per_page, total)
    return render_template("gestionar.html", gestiones=gestiones_paginado, tipificaciones=tipificaciones, pagination=pagination)


