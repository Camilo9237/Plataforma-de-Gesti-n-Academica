from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import os
from contextlib import contextmanager
from bson import ObjectId
from bson.timestamp import Timestamp
from datetime import datetime

class DatabaseConfig:
    """Configuración centralizada para la conexión a MongoDB"""
    
    # Configuración de la base de datos MongoDB
    DB_USER = os.getenv('MONGO_USER', '')
    DB_PASSWORD = os.getenv('MONGO_PASSWORD', '')
    DB_HOST = os.getenv('MONGO_HOST', 'localhost')
    DB_PORT = os.getenv('MONGO_PORT', '27017')
    DB_NAME = os.getenv('MONGO_DB_NAME', 'colegio')
    
    # String de conexión MongoDB
    if DB_USER and DB_PASSWORD:
        MONGO_URI = f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?authSource=admin"
    else:
        MONGO_URI = f"mongodb://{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Cliente de MongoDB
    client = None
    db = None
    
    @classmethod
    def initialize_connection(cls):
        """Inicializa la conexión a MongoDB"""
        try:
            cls.client = MongoClient(cls.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Verificar conexión
            cls.client.admin.command('ping')
            cls.db = cls.client[cls.DB_NAME]
            print(f"✓ Conexión a MongoDB establecida exitosamente")
            print(f"✓ Base de datos: {cls.DB_NAME}")
            return cls.db
        except ConnectionFailure as error:
            print(f"✗ Error al conectar con MongoDB: {error}")
            raise
    
    @classmethod
    def get_db(cls):
        """Obtiene la instancia de la base de datos"""
        if cls.db is None:
            cls.initialize_connection()
        return cls.db
    
    @classmethod
    def close_connection(cls):
        """Cierra la conexión a MongoDB"""
        if cls.client:
            cls.client.close()
            print("✓ Conexión a MongoDB cerrada")
    
    @classmethod
    def get_collection(cls, collection_name):
        """Obtiene una colección específica"""
        db = cls.get_db()
        return db[collection_name]


# Funciones de ayuda para operaciones comunes

def get_usuarios_collection():
    """Obtiene la colección de usuarios"""
    return DatabaseConfig.get_collection('usuarios')

def get_cursos_collection():
    """Obtiene la colección de cursos"""
    return DatabaseConfig.get_collection('cursos')

def get_matriculas_collection():
    """Obtiene la colección de matrículas"""
    return DatabaseConfig.get_collection('matriculas')

def get_reportes_collection():
    """Obtiene la colección de reportes"""
    return DatabaseConfig.get_collection('reportes')

def get_certificados_collection():
    """Obtiene la colección de certificados"""
    return DatabaseConfig.get_collection('certificados')


def get_auditoria_collection():
    """Obtiene la colección de auditoría"""
    return DatabaseConfig.get_collection('auditoria')


# Funciones de utilidad para conversión de datos

def serialize_doc(doc):
    """Convierte un documento MongoDB a formato JSON serializable"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Timestamp):
                # Convertir Timestamp a datetime y luego a ISO string
                result[key] = datetime.fromtimestamp(value.time).isoformat()
            elif isinstance(value, (dict, list)):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    return doc


def string_to_objectid(id_string):
    """Convierte un string a ObjectId de MongoDB"""
    try:
        if isinstance(id_string, ObjectId):
            return id_string
        return ObjectId(id_string)
    except:
        return None


def registrar_auditoria(id_usuario, accion, entidad_afectada, id_entidad=None, detalles=None):
    """Registra una acción en la auditoría"""
    try:
        auditoria = get_auditoria_collection()
        documento = {
            'id_usuario': string_to_objectid(id_usuario) if id_usuario else None,
            'accion': accion,
            'entidad_afectada': entidad_afectada,
            'id_entidad': string_to_objectid(id_entidad) if id_entidad else None,
            'detalles': detalles,
            'fecha': datetime.utcnow()
        }
        auditoria.insert_one(documento)
    except Exception as e:
        print(f"Error al registrar auditoría: {e}")
