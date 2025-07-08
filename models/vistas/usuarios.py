from flask import Flask, Blueprint, render_template, request
from database.config import db
from sqlalchemy import text
from auth.decorators import *
import math  # Necesario para math.ceil

def datos_usuarios(page=1, per_page=10):
    try:
        offset = (page - 1) * per_page
        datos = db.session.execute(text("SELECT * FROM usuarios LIMIT :limit OFFSET :offset"), {"limit": per_page, "offset": offset}).fetchall()
        total = db.session.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
        return datos, total
    except Exception as e:
        print(f"Error: {e}")
        return [], 0

vista_usuarios = Blueprint('vista_usuarios', __name__)


# Clase de Paginación (asegúrate de que esté definida antes de usarla)
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
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

@vista_usuarios.route("/usuarios")
@login_required
@role_required(1)
def tabla_usuarios():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    usuarios, total = datos_usuarios(page, per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total)
    return render_template("usuarios.html", 
                         usuarios=usuarios,
                         pagination=pagination)