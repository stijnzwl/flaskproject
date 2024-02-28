from flask import Blueprint

bp = Blueprint('casino', __name__)

from app.casino import routes