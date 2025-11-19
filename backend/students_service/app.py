from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime
from keycloak import KeycloakOpenID
from functools import wraps
import sys
import os
from bson.timestamp import Timestamp

# Agregar el path del backend para importar db_config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_config import (
    get_usuarios_collection,
    get_matriculas_collection,
    serialize_doc,
    string_to_objectid,
    registrar_auditoria
)

app = Flask(__name__)
app.secret_key = "PlataformaColegios"
CORS(app)

keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8082",
    client_id="01",
    realm_name="platamaformaInstitucional",
    client_secret_key="2m2KWH4lyYgh9CwoM1y2QI6bFrDjR3OV"
)

def tiene_rol(token_info, cliente_id, rol_requerido):
    try:
        # Revisar roles a nivel de realm
        realm_roles = token_info.get("realm_access", {}).get("roles", [])
        if rol_requerido in realm_roles:
            return True

        # Revisar roles a nivel de cliente (resource_access)
        resource_roles = token_info.get("resource_access", {}).get(cliente_id, {}).get("roles", [])
        if rol_requerido in resource_roles:
            return True

        return False
    except Exception:
        return False

def token_required(rol_requerido):
    def decorator(f):
        @wraps(f)
        def decorated (*args, **kwargs):
            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                return jsonify({"error": "Token Requerido"}), 401
            
            try:
                token = auth_header.split(" ")[1]
                userinfo = keycloak_openid.decode_token(token)
            except Exception as e:
                return jsonify({"error": "Token inválido o expirado"}), 401
            if not tiene_rol(userinfo, keycloak_openid.client_id, rol_requerido):
                return jsonify({"error": f"Acceso denegado: se requiere el rol '{rol_requerido}'"}), 403
            # guardar información del usuario en 'g' para que la función pueda acceder si lo necesita
            g.userinfo = userinfo
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/')
def home():
    return jsonify({
        'service': 'Students Service',
        'version': '2.0.0',
        'database': 'MongoDB',
        'endpoints': {
            'get_all': 'GET /students',
            'get_one': 'GET /students/{id}',
            'create': 'POST /students',
            'update': 'PUT /students/{id}',
            'delete': 'DELETE /students/{id}',
            'grades': 'GET /students/{id}/grades',
            'enrollments': 'GET /students/{id}/enrollments'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'students', 'database': 'MongoDB'})

@app.route('/students', methods=['GET'])
def get_students():
    """Obtener todos los estudiantes"""
    try:
        usuarios = get_usuarios_collection()
        
        # Filtros opcionales
        grado = request.args.get('grado') or request.args.get('grade')
        status = request.args.get('status')
        
        # Construir query
        query = {'rol': 'estudiante'}
        
        if status:
            query['activo'] = (status.lower() == 'active')
        
        # Buscar estudiantes
        estudiantes = list(usuarios.find(query))
        
        # Serializar documentos
        estudiantes_serializados = serialize_doc(estudiantes)
        
        return jsonify({
            'success': True,
            'data': estudiantes_serializados,
            'count': len(estudiantes_serializados)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Obtener un estudiante por ID"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Buscar estudiante
        estudiante = usuarios.find_one({'_id': obj_id, 'rol': 'estudiante'})
        
        if not estudiante:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': serialize_doc(estudiante)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/students', methods=['POST'])
def create_student():
    """Crear un nuevo estudiante"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400
        
        # Validar campos requeridos
        required_fields = ['correo', 'nombres', 'apellidos']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400

        usuarios = get_usuarios_collection()
        
        # Verificar si el correo ya existe
        if usuarios.find_one({'correo': data['correo']}):
            return jsonify({
                'success': False,
                'error': 'El correo ya está registrado'
            }), 400
        
        # Crear documento del estudiante
        nuevo_estudiante = {
            'correo': data['correo'],
            'rol': 'estudiante',
            'nombres': data['nombres'],
            'apellidos': data['apellidos'],
            'creado_en': Timestamp(int(datetime.utcnow().timestamp()), 0),
            'activo': data.get('activo', True)
        }
        
        # Campos opcionales específicos de estudiante
        if 'codigo_est' in data:
            nuevo_estudiante['codigo_est'] = data['codigo_est']
        if 'fecha_nacimiento' in data:
            nuevo_estudiante['fecha_nacimiento'] = datetime.fromisoformat(data['fecha_nacimiento'].replace('Z', '+00:00'))
        if 'direccion' in data:
            nuevo_estudiante['direccion'] = data['direccion']
        if 'telefono' in data:
            nuevo_estudiante['telefono'] = data['telefono']
        if 'nombre_acudiente' in data:
            nuevo_estudiante['nombre_acudiente'] = data['nombre_acudiente']
        if 'telefono_acudiente' in data:
            nuevo_estudiante['telefono_acudiente'] = data['telefono_acudiente']
        
        # Insertar en la base de datos
        resultado = usuarios.insert_one(nuevo_estudiante)
        
        # Registrar en auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='crear_estudiante',
            entidad_afectada='usuarios',
            id_entidad=str(resultado.inserted_id),
            detalles=f"Estudiante creado: {data['nombres']} {data['apellidos']}"
        )
        
        # Obtener el documento insertado
        estudiante_creado = usuarios.find_one({'_id': resultado.inserted_id})
        
        return jsonify({
            'success': True,
            'message': 'Estudiante creado exitosamente',
            'data': serialize_doc(estudiante_creado)
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Actualizar un estudiante"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400
        
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Verificar que el estudiante existe
        estudiante_existente = usuarios.find_one({'_id': obj_id, 'rol': 'estudiante'})
        if not estudiante_existente:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
        
        # Preparar datos para actualizar
        campos_no_modificables = {'_id', 'rol', 'creado_en', 'correo'}
        datos_actualizacion = {k: v for k, v in data.items() if k not in campos_no_modificables}
        
        # Convertir fecha_nacimiento si viene en el request
        if 'fecha_nacimiento' in datos_actualizacion:
            datos_actualizacion['fecha_nacimiento'] = datetime.fromisoformat(
                datos_actualizacion['fecha_nacimiento'].replace('Z', '+00:00')
            )
        
        # Actualizar
        resultado = usuarios.update_one(
            {'_id': obj_id},
            {'$set': datos_actualizacion}
        )
        
        if resultado.modified_count > 0:
            # Registrar en auditoría
            registrar_auditoria(
                id_usuario=None,
                accion='actualizar_estudiante',
                entidad_afectada='usuarios',
                id_entidad=student_id,
                detalles=f"Campos actualizados: {', '.join(datos_actualizacion.keys())}"
            )
            
            # Obtener documento actualizado
            estudiante_actualizado = usuarios.find_one({'_id': obj_id})
            
            return jsonify({
                'success': True,
                'message': 'Estudiante actualizado exitosamente',
                'data': serialize_doc(estudiante_actualizado)
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'No se realizaron cambios',
                'data': serialize_doc(estudiante_existente)
            }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Eliminar (desactivar) un estudiante"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Verificar que el estudiante existe
        estudiante = usuarios.find_one({'_id': obj_id, 'rol': 'estudiante'})
        if not estudiante:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
        
        # Desactivar
        resultado = usuarios.update_one(
            {'_id': obj_id},
            {'$set': {'activo': False}}
        )
        
        # Registrar en auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='desactivar_estudiante',
            entidad_afectada='usuarios',
            id_entidad=student_id,
            detalles=f"Estudiante desactivado: {estudiante['nombres']} {estudiante['apellidos']}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Estudiante desactivado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/students/<student_id>/grades', methods=['GET'])
def get_student_grades(student_id):
    """Obtener calificaciones de un estudiante"""
    try:
        matriculas = get_matriculas_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Buscar matrículas del estudiante
        student_matriculas = list(matriculas.find({'id_estudiante': obj_id}))
        
        return jsonify({
            'success': True,
            'data': serialize_doc(student_matriculas),
            'count': len(student_matriculas)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/students/<student_id>/enrollments', methods=['GET'])
def get_student_enrollments(student_id):
    """Obtener inscripciones de un estudiante"""
    try:
        matriculas = get_matriculas_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Buscar matrículas activas del estudiante
        enrollments = list(matriculas.find({
            'id_estudiante': obj_id,
            'estado': 'activo'
        }))
        
        return jsonify({
            'success': True,
            'data': serialize_doc(enrollments),
            'count': len(enrollments)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)