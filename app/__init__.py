import sqlite3
from app.session_decorators import nocache

def get_db_connection(timeout=5):
    conn = sqlite3.connect('gestor_de_tareas.db', timeout=timeout)
    conn.row_factory = sqlite3.Row
    return conn

# Export nocache for use in other modules
__all__ = ['get_db_connection', 'nocache']
