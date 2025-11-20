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
    get_cursos_collection,
    get_matriculas_collection,
    serialize_doc,
    string_to_objectid,
    registrar_auditoria
)

app = Flask(__name__)
app.secret_key = "PlataformaColegios"

# 🔧 CORS CONFIGURACIÓN COMPLETA
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:4200"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = {
            'Access-Control-Allow-Origin': 'http://localhost:4200',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        response.headers.update(headers)
        return response

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
        'service': 'Teachers Service',
        'version': '2.0.0',
        'database': 'MongoDB',
        'endpoints': {
            'get_all': 'GET /teachers',
            'get_one': 'GET /teachers/{id}',
            'create': 'POST /teachers',
            'update': 'PUT /teachers/{id}',
            'delete': 'DELETE /teachers/{id}',
            'by_subject': 'GET /teachers?subject={subject}'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'teachers', 'database': 'MongoDB'})

@app.route('/teachers', methods=['GET'])
def get_teachers():
    """Obtener todos los profesores"""
    try:
        usuarios = get_usuarios_collection()
        
        # Filtros opcionales
        especialidad = request.args.get('especialidad') or request.args.get('subject')
        status = request.args.get('status')
        
        # Construir query
        query = {'rol': 'docente'}
        
        if status:
            query['activo'] = (status.lower() == 'active')
        
        if especialidad:
            query['especialidad'] = {'$regex': especialidad, '$options': 'i'}
        
        # Buscar docentes
        docentes = list(usuarios.find(query))
        
        # Serializar documentos
        docentes_serializados = serialize_doc(docentes)
        
        return jsonify({
            'success': True,
            'data': docentes_serializados,
            'count': len(docentes_serializados)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    """Obtener un profesor por ID"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(teacher_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Buscar docente
        docente = usuarios.find_one({'_id': obj_id, 'rol': 'docente'})
        
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': serialize_doc(docente)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teachers', methods=['POST'])
def create_teacher():
    """Crear un nuevo profesor"""
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
        
        # Crear documento del docente
        nuevo_docente = {
            'correo': data['correo'],
            'rol': 'docente',
            'nombres': data['nombres'],
            'apellidos': data['apellidos'],
            'creado_en': Timestamp(int(datetime.utcnow().timestamp()), 0),
            'activo': data.get('activo', True)
        }
        
        # Campos opcionales específicos de docente
        if 'telefono' in data:
            nuevo_docente['telefono'] = data['telefono']
        if 'codigo_empleado' in data:
            nuevo_docente['codigo_empleado'] = data['codigo_empleado']
        if 'especialidad' in data:
            nuevo_docente['especialidad'] = data['especialidad']
        if 'fecha_ingreso' in data:
            nuevo_docente['fecha_ingreso'] = datetime.fromisoformat(data['fecha_ingreso'].replace('Z', '+00:00'))
        
        # Insertar en la base de datos
        resultado = usuarios.insert_one(nuevo_docente)
        
        # Registrar en auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='crear_docente',
            entidad_afectada='usuarios',
            id_entidad=str(resultado.inserted_id),
            detalles=f"Docente creado: {data['nombres']} {data['apellidos']}"
        )
        
        # Obtener el documento insertado
        docente_creado = usuarios.find_one({'_id': resultado.inserted_id})
        
        return jsonify({
            'success': True,
            'message': 'Docente creado exitosamente',
            'data': serialize_doc(docente_creado)
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    """Actualizar un profesor"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400
        
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(teacher_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Verificar que el docente existe
        docente_existente = usuarios.find_one({'_id': obj_id, 'rol': 'docente'})
        if not docente_existente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        # Preparar datos para actualizar (excluir campos que no se deben modificar)
        campos_no_modificables = {'_id', 'rol', 'creado_en', 'correo'}
        datos_actualizacion = {k: v for k, v in data.items() if k not in campos_no_modificables}
        
        # Convertir fecha_ingreso si viene en el request
        if 'fecha_ingreso' in datos_actualizacion:
            datos_actualizacion['fecha_ingreso'] = datetime.fromisoformat(
                datos_actualizacion['fecha_ingreso'].replace('Z', '+00:00')
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
                accion='actualizar_docente',
                entidad_afectada='usuarios',
                id_entidad=teacher_id,
                detalles=f"Campos actualizados: {', '.join(datos_actualizacion.keys())}"
            )
            
            # Obtener documento actualizado
            docente_actualizado = usuarios.find_one({'_id': obj_id})
            
            return jsonify({
                'success': True,
                'message': 'Docente actualizado exitosamente',
                'data': serialize_doc(docente_actualizado)
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'No se realizaron cambios',
                'data': serialize_doc(docente_existente)
            }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Eliminar (desactivar) un profesor"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(teacher_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Verificar que el docente existe
        docente = usuarios.find_one({'_id': obj_id, 'rol': 'docente'})
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        # Desactivar (no eliminar físicamente)
        resultado = usuarios.update_one(
            {'_id': obj_id},
            {'$set': {'activo': False}}
        )
        
        # Registrar en auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='desactivar_docente',
            entidad_afectada='usuarios',
            id_entidad=teacher_id,
            detalles=f"Docente desactivado: {docente['nombres']} {docente['apellidos']}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Docente desactivado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/subjects', methods=['GET'])
def get_subjects():
    """Obtener lista de especialidades disponibles"""
    try:
        usuarios = get_usuarios_collection()
        
        # Obtener especialidades únicas de todos los docentes
        especialidades = usuarios.distinct('especialidad', {'rol': 'docente', 'especialidad': {'$exists': True, '$ne': None}})
        
        return jsonify({
            'success': True,
            'subjects': especialidades
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/groups', methods=['GET', 'OPTIONS'])
def teacher_groups():
    """Obtener grupos asignados al docente autenticado"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # TODO: Obtener teacher_id del token JWT
        # Por ahora usar ID de prueba o query param
        teacher_id = request.args.get('teacher_id', '673df447faf2a31cb63b0bb9')
        
        cursos = get_cursos_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(teacher_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        # Buscar cursos del docente
        grupos = list(cursos.find({'id_docente': obj_id, 'activo': True}))
        
        # Si no hay datos reales, devolver mock data
        if not grupos:
            mock_groups = {
                'success': True,
                'groups': [
                    {
                        '_id': '1',
                        'name': 'Matemáticas 10° A',
                        'students': 32,
                        'progress_pct': 65
                    },
                    {
                        '_id': '2',
                        'name': 'Física 11° B',
                        'students': 28,
                        'progress_pct': 58
                    },
                    {
                        '_id': '3',
                        'name': 'Matemáticas 9° C',
                        'students': 30,
                        'progress_pct': 72
                    }
                ]
            }
            return jsonify(mock_groups), 200
        
        # Transformar datos reales al formato esperado por el frontend
        grupos_formateados = []
        for grupo in grupos:
            # Contar estudiantes matriculados
            matriculas = get_matriculas_collection()
            num_estudiantes = matriculas.count_documents({
                'id_curso': grupo['_id'],
                'estado': 'activo'
            })
            
            grupos_formateados.append({
                '_id': str(grupo['_id']),
                'name': f"{grupo.get('nombre_curso', 'Curso')} {grupo.get('grado', '')}",
                'students': num_estudiantes,
                'progress_pct': 50  # TODO: Calcular progreso real
            })
        
        return jsonify({
            'success': True,
            'groups': grupos_formateados
        }), 200
        
    except Exception as e:
        print(f"Error en /teacher/groups: {e}")
        import traceback
        traceback.print_exc()
        
        # Devolver mock data en caso de error
        return jsonify({
            'success': True,
            'groups': [
                {'_id': '1', 'name': 'Matemáticas 10° A', 'students': 32, 'progress_pct': 65},
                {'_id': '2', 'name': 'Física 11° B', 'students': 28, 'progress_pct': 58}
            ]
        }), 200
@app.route('/teacher/pending-grades')
def teacher_pending_grades():
    """Calificaciones pendientes (mock por ahora)"""
    pending = [
        {'course': "Matemáticas 10°A", 'pending': 12},
        {'course': "Física 11°B", 'pending': 8},
        {'course': "Matemáticas 9°C", 'pending': 5}
    ]
    return jsonify(pending), 200

@app.route('/teacher/overview')
def teacher_overview():
    """Resumen del docente (mock por ahora)"""
    overview = {
        'groups_count': 3,
        'pending_grades': 25,
        'next_event': 'Entrega de notas el viernes'
    }
    return jsonify(overview), 200

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)