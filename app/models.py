from flask_login import UserMixin
import sqlite3

class Usuario(UserMixin):
    def __init__(self, id, nombre_completo, nombre_usuario, documento, correo, contraseña, rol, estado, grupo=None):
        self.id = id
        self.nombre_completo = nombre_completo
        self.nombre_usuario = nombre_usuario
        self.documento = documento
        self.correo = correo
        self.contraseña = contraseña
        self.rol = rol
        self.estado = estado
        self.grupo = grupo

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.estado == 'activo'

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('gestor_de_tareas.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuario WHERE id = ?', (user_id,))
        usuario_data = cursor.fetchone()
        conn.close()
        
        if usuario_data:
            return Usuario(
                id=usuario_data['id'],
                nombre_completo=usuario_data['nombre_completo'],
                nombre_usuario=usuario_data['nombre_usuario'],
                documento=usuario_data['documento'],
                correo=usuario_data['correo'],
                contraseña=usuario_data['contraseña'],
                rol=usuario_data['rol'],
                estado=usuario_data['estado'],
                grupo=usuario_data['grupo']
            )
        return None

    @staticmethod
    def get_by_username(nombre_usuario):
        conn = sqlite3.connect('gestor_de_tareas.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuario WHERE nombre_usuario = ?', (nombre_usuario,))
        usuario_data = cursor.fetchone()
        conn.close()
        
        if usuario_data:
            return Usuario(
                id=usuario_data['id'],
                nombre_completo=usuario_data['nombre_completo'],
                nombre_usuario=usuario_data['nombre_usuario'],
                documento=usuario_data['documento'],
                correo=usuario_data['correo'],
                contraseña=usuario_data['contraseña'],
                rol=usuario_data['rol'],
                estado=usuario_data['estado'],
                grupo=usuario_data['grupo']
            )
        return None
