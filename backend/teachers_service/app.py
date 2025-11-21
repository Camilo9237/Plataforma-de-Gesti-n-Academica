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
    get_asistencia_collection,
    get_observaciones_collection, 
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
    realm_name="plataformaInstitucional",
    client_secret_key="wP8EhQnsdaYcCSyFTnD2wu4n0dssApUz"
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
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                print("❌ No se encontró header Authorization")
                return jsonify({"error": "Token Requerido"}), 401
            
            try:
                token = auth_header.split(" ")[1]
                print(f"🔑 Token recibido: {token[:50]}...")
                
                # 🔧 MODO DESARROLLO: Aceptar tokens mock
                if token.startswith('mock-token-') or token.startswith('eyJ'):
                    # Para tokens mock de desarrollo
                    if token.startswith('mock-token-'):
                        print("⚠️ Usando token mock de desarrollo")
                        g.userinfo = {'sub': 'dev-docente', 'roles': [rol_requerido]}
                        return f(*args, **kwargs)
                    
                    # Para tokens JWT reales, intentar decodificar
                    try:
                        userinfo = keycloak_openid.decode_token(
                        token,
                        key=keycloak_openid.public_key(),
                        options={
                            "verify_signature": True,
                            "verify_aud": False,
                            "verify_exp": True
                        }
                )
                        print(f"✅ Token decodificado correctamente")
                        print(f"   Usuario: {userinfo.get('preferred_username', 'N/A')}")
                        print(f"   Roles: {userinfo.get('realm_access', {}).get('roles', [])}")
                    except Exception as decode_error:
                        print(f"⚠️ Error decodificando con Keycloak: {decode_error}")
                        # Intentar decodificar sin verificar firma (solo para desarrollo)
                        import jwt as pyjwt
                        try:
                            userinfo = pyjwt.decode(token, options={"verify_signature": False})
                            print("⚠️ Token decodificado SIN verificar firma (modo desarrollo)")
                        except Exception as jwt_error:
                            print(f"❌ Error decodificando JWT: {jwt_error}")
                            return jsonify({"error": "Token inválido o expirado"}), 401
                else:
                    userinfo = keycloak_openid.decode_token(token)
                
            except IndexError:
                print("❌ Formato de Authorization header inválido")
                return jsonify({"error": "Formato de token inválido"}), 401
            except Exception as e:
                print(f"❌ Error procesando token: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": "Token inválido o expirado"}), 401
            
            # Verificar rol
            if not tiene_rol(userinfo, keycloak_openid.client_id, rol_requerido):
                print(f"❌ Acceso denegado: se requiere rol '{rol_requerido}'")
                print(f"   Roles encontrados: {userinfo.get('realm_access', {}).get('roles', [])}")
                return jsonify({"error": f"Acceso denegado: se requiere el rol '{rol_requerido}'"}), 403
            
            print(f"✅ Acceso permitido para rol '{rol_requerido}'")
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
@token_required('docente')
def teacher_groups():
    """Obtener grupos asignados al docente autenticado"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # 🔧 Obtener email del token (preferiblemente) o sub como fallback
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        print(f"🔍 Buscando docente con email: {teacher_email}, sub: {teacher_sub}")
        
        usuarios = get_usuarios_collection()
        
        # Buscar por email primero
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        # Si no se encuentra por email, intentar por sub (si está guardado en la BD)
        if not docente:
            docente = usuarios.find_one({
                'keycloak_id': teacher_sub,  # Asumiendo que guardas el UUID aquí
                'rol': 'docente',
                'activo': True
            })
        
        if not docente:
            print(f"❌ Docente no encontrado. Email buscado: {teacher_email}")
            return jsonify({
                'success': False,
                'error': 'Docente no encontrado en la base de datos'
            }), 404
        
        print(f"✅ Docente encontrado: {docente.get('nombres')} {docente.get('apellidos')}")
                
        cursos = get_cursos_collection()
        matriculas = get_matriculas_collection()
        
        # Buscar cursos del docente
        grupos = list(cursos.find({
            'id_docente': docente['_id'],
            'activo': True
        }))
        
        # Transformar datos al formato esperado por el frontend
        grupos_formateados = []
        for grupo in grupos:
            # Contar estudiantes matriculados activos
            num_estudiantes = matriculas.count_documents({
                'id_curso': grupo['_id'],
                'estado': 'activo'
            })
            
            # Contar estudiantes con calificaciones completas para calcular progreso
            estudiantes_con_calificaciones = matriculas.count_documents({
                'id_curso': grupo['_id'],
                'estado': 'activo',
                'calificaciones': {'$exists': True, '$ne': []}
            })
            
            # Calcular porcentaje de progreso
            progress_pct = 0
            if num_estudiantes > 0:
                progress_pct = round((estudiantes_con_calificaciones / num_estudiantes) * 100)
            
            grupos_formateados.append({
                '_id': str(grupo['_id']),
                'name': f"{grupo.get('nombre_curso', 'Curso')} - {grupo.get('grado', '')}° ({grupo.get('periodo', '')})",
                'students': num_estudiantes,
                'progress_pct': progress_pct,
                'codigo': grupo.get('codigo_curso', ''),
                'periodo': grupo.get('periodo', '')
            })
        
        return jsonify({
            'success': True,
            'groups': grupos_formateados,
            'count': len(grupos_formateados)
        }), 200
        
    except Exception as e:
        print(f"❌ Error en /teacher/groups: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/teacher/pending-grades', methods=['GET'])
@token_required('docente')
def teacher_pending_grades():
    """Calificaciones pendientes del docente autenticado"""
    try:
        # 🔧 Obtener email del token (preferiblemente) o sub como fallback
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        print(f"🔍 Buscando docente con email: {teacher_email}, sub: {teacher_sub}")
        
        usuarios = get_usuarios_collection()
        
        # Buscar por email primero
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        # Si no se encuentra por email, intentar por sub (si está guardado en la BD)
        if not docente:
            docente = usuarios.find_one({
                'keycloak_id': teacher_sub,  # Asumiendo que guardas el UUID aquí
                'rol': 'docente',
                'activo': True
            })
        
        if not docente:
            print(f"❌ Docente no encontrado. Email buscado: {teacher_email}")
            return jsonify({
                'success': False,
                'error': 'Docente no encontrado en la base de datos'
            }), 404
        
        print(f"✅ Docente encontrado: {docente.get('nombres')} {docente.get('apellidos')}")
     
        cursos = get_cursos_collection()
        matriculas = get_matriculas_collection()
        
        # Obtener cursos del docente
        cursos_docente = list(cursos.find({
            'id_docente': docente['_id'],
            'activo': True
        }))
        
        pending_list = []
        
        for curso in cursos_docente:
            # Total de estudiantes en el curso
            total_estudiantes = matriculas.count_documents({
                'id_curso': curso['_id'],
                'estado': 'activo'
            })
            
            # Estudiantes con calificaciones
            estudiantes_con_notas = matriculas.count_documents({
                'id_curso': curso['_id'],
                'estado': 'activo',
                'calificaciones': {'$exists': True, '$ne': []}
            })
            
            # Estudiantes sin calificaciones
            pending_count = total_estudiantes - estudiantes_con_notas
            
            if pending_count > 0:
                pending_list.append({
                    'course': f"{curso.get('nombre_curso', '')} - {curso.get('grado', '')}°",
                    'pending': pending_count,
                    'total': total_estudiantes,
                    'course_id': str(curso['_id'])
                })
        
        return jsonify({
            'success': True,
            'pending': pending_list,
            'total_pending': sum(p['pending'] for p in pending_list)
        }), 200
        
    except Exception as e:
        print(f"❌ Error en /teacher/pending-grades: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/overview', methods=['GET'])
@token_required('docente')
def teacher_overview():
    """Resumen general del docente autenticado"""
    try:
        # 🔧 Obtener email del token (preferiblemente) o sub como fallback
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        print(f"🔍 Buscando docente con email: {teacher_email}, sub: {teacher_sub}")
        
        usuarios = get_usuarios_collection()
        
        # Buscar por email primero
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        # Si no se encuentra por email, intentar por sub (si está guardado en la BD)
        if not docente:
            docente = usuarios.find_one({
                'keycloak_id': teacher_sub,  # Asumiendo que guardas el UUID aquí
                'rol': 'docente',
                'activo': True
            })
        
        if not docente:
            print(f"❌ Docente no encontrado. Email buscado: {teacher_email}")
            return jsonify({
                'success': False,
                'error': 'Docente no encontrado en la base de datos'
            }), 404
        
        print(f"✅ Docente encontrado: {docente.get('nombres')} {docente.get('apellidos')}")
     
        cursos = get_cursos_collection()
        matriculas = get_matriculas_collection()
        
        # Contar grupos activos
        groups_count = cursos.count_documents({
            'id_docente': docente['_id'],
            'activo': True
        })
        
        # Contar calificaciones pendientes
        cursos_docente = list(cursos.find({
            'id_docente': docente['_id'],
            'activo': True
        }))
        
        total_pending = 0
        total_estudiantes = 0
        
        for curso in cursos_docente:
            total = matriculas.count_documents({
                'id_curso': curso['_id'],
                'estado': 'activo'
            })
            
            con_notas = matriculas.count_documents({
                'id_curso': curso['_id'],
                'estado': 'activo',
                'calificaciones': {'$exists': True, '$ne': []}
            })
            
            total_estudiantes += total
            total_pending += (total - con_notas)
        
        # Buscar próximo evento (última fecha de evaluación registrada)
        pipeline = [
            {'$match': {'id_curso': {'$in': [c['_id'] for c in cursos_docente]}}},
            {'$unwind': '$calificaciones'},
            {'$sort': {'calificaciones.fecha_eval': -1}},
            {'$limit': 1}
        ]
        
        ultima_eval = list(matriculas.aggregate(pipeline))
        
        next_event = 'No hay eventos programados'
        if ultima_eval and len(ultima_eval) > 0:
            fecha_ultima = ultima_eval[0]['calificaciones'].get('fecha_eval')
            if fecha_ultima:
                next_event = f"Última evaluación: {fecha_ultima.strftime('%d/%m/%Y')}"
        
        return jsonify({
            'success': True,
            'groups_count': groups_count,
            'pending_grades': total_pending,
            'total_students': total_estudiantes,
            'next_event': next_event,
            'teacher_name': f"{docente.get('nombres', '')} {docente.get('apellidos', '')}",
            'especialidad': docente.get('especialidad', 'N/A')
        }), 200
        
    except Exception as e:
        print(f"❌ Error en /teacher/overview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/courses/<course_id>/grades', methods=['GET'])
@token_required('docente')
def get_course_grades(course_id):
    """Obtener calificaciones de un curso del docente"""
    try:
        matriculas = get_matriculas_collection()
        cursos = get_cursos_collection()
        
        # Convertir ID a ObjectId
        curso_obj_id = string_to_objectid(course_id)
        if not curso_obj_id:
            return jsonify({'success': False, 'error': 'ID de curso inválido'}), 400
        
        # Verificar que el curso existe
        curso = cursos.find_one({'_id': curso_obj_id})
        if not curso:
            return jsonify({'success': False, 'error': 'Curso no encontrado'}), 404
        
        # 🔧 ACTUALIZACIÓN: Extraer email del token correctamente
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        print(f"🔍 Verificando permisos del docente:")
        print(f"   Email del token: {teacher_email}")
        print(f"   Sub del token: {teacher_sub}")
        print(f"   ID del curso: {course_id}")
        
        usuarios = get_usuarios_collection()
        
        # Buscar por email primero
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        # Si no se encuentra por email, intentar por keycloak_id
        if not docente:
            docente = usuarios.find_one({
                'keycloak_id': teacher_sub,
                'rol': 'docente',
                'activo': True
            })
        
        if not docente:
            print(f"❌ Docente no encontrado en la base de datos")
            print(f"   Email buscado: {teacher_email}")
            print(f"   Sub buscado: {teacher_sub}")
            return jsonify({
                'success': False,
                'error': 'Docente no encontrado en la base de datos'
            }), 404
        
        print(f"✅ Docente encontrado: {docente.get('nombres')} {docente.get('apellidos')}")
        print(f"   ID del docente en BD: {docente['_id']}")
        print(f"   ID del docente del curso: {curso.get('id_docente')}")
        
        # Verificar que el curso pertenece al docente
        if curso.get('id_docente') != docente['_id']:
            print(f"❌ El curso no pertenece a este docente")
            print(f"   Se esperaba: {curso.get('id_docente')}")
            print(f"   Se recibió: {docente['_id']}")
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para ver este curso'
            }), 403
        
        print(f"✅ Permisos verificados correctamente")
        
        # Buscar matrículas del curso
        enrollments = list(matriculas.find({
            'id_curso': curso_obj_id,
            'estado': 'activo'
        }))
        
        print(f"📊 Encontradas {len(enrollments)} matrículas activas")
        
        # Formatear datos de estudiantes con calificaciones
        students_data = []
        for enrollment in enrollments:
            student_info = enrollment.get('estudiante_info', {})
            calificaciones = enrollment.get('calificaciones', [])
            
            # Calcular promedio ponderado
            promedio = 0
            if calificaciones:
                total = sum(c.get('nota', 0) * c.get('peso', 0) for c in calificaciones)
                total_peso = sum(c.get('peso', 0) for c in calificaciones)
                promedio = round(total / total_peso, 2) if total_peso > 0 else 0
            
            students_data.append({
                'enrollment_id': str(enrollment['_id']),
                'student_id': str(enrollment['id_estudiante']),
                'student_name': f"{student_info.get('nombres', '')} {student_info.get('apellidos', '')}",
                'student_code': student_info.get('codigo_est', ''),
                'grades': serialize_doc(calificaciones),
                'average': promedio,
                'estado': 'Aprobado' if promedio >= 3.0 else 'Reprobado'
            })
        
        return jsonify({
            'success': True,
            'course_id': course_id,
            'course_name': curso.get('nombre_curso', ''),
            'course_code': curso.get('codigo_curso', ''),
            'grado': curso.get('grado', ''),
            'periodo': curso.get('periodo', ''),
            'students': students_data,
            'count': len(students_data)
        }), 200
        
    except Exception as e:
        print(f"❌ Error en get_course_grades: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500    
@app.route('/teacher/grades', methods=['POST'])
@token_required('docente')
def add_grade():
    """Agregar una calificación a un estudiante"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400
        
        # Validar campos requeridos
        required_fields = ['enrollment_id', 'tipo', 'nota', 'peso']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Validar nota
        nota = float(data['nota'])
        nota_maxima = float(data.get('nota_maxima', 5.0))
        peso = float(data['peso'])
        
        if nota < 0 or nota > nota_maxima:
            return jsonify({
                'success': False,
                'error': f'La nota debe estar entre 0 y {nota_maxima}'
            }), 400
        
        if peso < 0 or peso > 1:
            return jsonify({
                'success': False,
                'error': 'El peso debe estar entre 0 y 1'
            }), 400
        
        matriculas = get_matriculas_collection()
        
        enrollment_obj_id = string_to_objectid(data['enrollment_id'])
        if not enrollment_obj_id:
            return jsonify({'success': False, 'error': 'ID de matrícula inválido'}), 400
        
        matricula = matriculas.find_one({'_id': enrollment_obj_id})
        if not matricula:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        # Crear calificación
        nueva_calificacion = {
            'tipo': data['tipo'],
            'nota': nota,
            'nota_maxima': nota_maxima,
            'peso': peso,
            'fecha_eval': datetime.utcnow(),
            'comentarios': data.get('comentarios', '')
        }
        
        # Agregar calificación
        matriculas.update_one(
            {'_id': enrollment_obj_id},
            {'$push': {'calificaciones': nueva_calificacion}}
        )
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=g.userinfo.get('sub'),
            accion='agregar_calificacion',
            entidad_afectada='matriculas',
            id_entidad=data['enrollment_id'],
            detalles=f"Calificación agregada: {data['tipo']} - Nota: {nota}"
        )
        
        matricula_actualizada = matriculas.find_one({'_id': enrollment_obj_id})
        
        return jsonify({
            'success': True,
            'message': 'Calificación agregada exitosamente',
            'enrollment': serialize_doc(matricula_actualizada)
        }), 201
        
    except ValueError:
        return jsonify({'success': False, 'error': 'Valores numéricos inválidos'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/grades/<enrollment_id>', methods=['PUT'])
@token_required('docente')
def update_grade(enrollment_id):
    """Actualizar una calificación específica"""
    try:
        data = request.get_json()
        
        if not data or 'grade_index' not in data:
            return jsonify({'success': False, 'error': 'Se requiere grade_index'}), 400
        
        grade_index = int(data['grade_index'])
        matriculas = get_matriculas_collection()
        
        enrollment_obj_id = string_to_objectid(enrollment_id)
        if not enrollment_obj_id:
            return jsonify({'success': False, 'error': 'ID de matrícula inválido'}), 400
        
        matricula = matriculas.find_one({'_id': enrollment_obj_id})
        if not matricula:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        calificaciones = matricula.get('calificaciones', [])
        if grade_index < 0 or grade_index >= len(calificaciones):
            return jsonify({'success': False, 'error': 'Índice de calificación inválido'}), 400
        
        # Construir actualización
        update_fields = {}
        
        if 'nota' in data:
            nota = float(data['nota'])
            nota_maxima = calificaciones[grade_index].get('nota_maxima', 5.0)
            if nota < 0 or nota > nota_maxima:
                return jsonify({
                    'success': False,
                    'error': f'La nota debe estar entre 0 y {nota_maxima}'
                }), 400
            update_fields[f'calificaciones.{grade_index}.nota'] = nota
        
        if 'peso' in data:
            peso = float(data['peso'])
            if peso < 0 or peso > 1:
                return jsonify({'success': False, 'error': 'El peso debe estar entre 0 y 1'}), 400
            update_fields[f'calificaciones.{grade_index}.peso'] = peso
        
        if 'comentarios' in data:
            update_fields[f'calificaciones.{grade_index}.comentarios'] = data['comentarios']
        
        if 'tipo' in data:
            update_fields[f'calificaciones.{grade_index}.tipo'] = data['tipo']
        
        if update_fields:
            matriculas.update_one(
                {'_id': enrollment_obj_id},
                {'$set': update_fields}
            )
            
            registrar_auditoria(
                id_usuario=g.userinfo.get('sub'),
                accion='actualizar_calificacion',
                entidad_afectada='matriculas',
                id_entidad=enrollment_id,
                detalles=f"Calificación actualizada en índice {grade_index}"
            )
        
        matricula_actualizada = matriculas.find_one({'_id': enrollment_obj_id})
        
        return jsonify({
            'success': True,
            'message': 'Calificación actualizada exitosamente',
            'enrollment': serialize_doc(matricula_actualizada)
        }), 200
        
    except ValueError:
        return jsonify({'success': False, 'error': 'Valores numéricos inválidos'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/grades/<enrollment_id>/<int:grade_index>', methods=['DELETE'])
@token_required('docente')
def delete_grade(enrollment_id, grade_index):
    """Eliminar una calificación específica"""
    try:
        matriculas = get_matriculas_collection()
        
        enrollment_obj_id = string_to_objectid(enrollment_id)
        if not enrollment_obj_id:
            return jsonify({'success': False, 'error': 'ID de matrícula inválido'}), 400
        
        matricula = matriculas.find_one({'_id': enrollment_obj_id})
        if not matricula:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        calificaciones = matricula.get('calificaciones', [])
        if grade_index < 0 or grade_index >= len(calificaciones):
            return jsonify({'success': False, 'error': 'Índice de calificación inválido'}), 400
        
        calificaciones.pop(grade_index)
        
        matriculas.update_one(
            {'_id': enrollment_obj_id},
            {'$set': {'calificaciones': calificaciones}}
        )
        
        registrar_auditoria(
            id_usuario=g.userinfo.get('sub'),
            accion='eliminar_calificacion',
            entidad_afectada='matriculas',
            id_entidad=enrollment_id,
            detalles=f"Calificación eliminada en índice {grade_index}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Calificación eliminada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/grades/bulk', methods=['POST'])
@token_required('docente')
def bulk_upload_grades():
    """Carga masiva de calificaciones para un curso"""
    try:
        data = request.get_json()
        
        if not data or 'grades' not in data:
            return jsonify({'success': False, 'error': 'No se proporcionaron calificaciones'}), 400
        
        course_id = data.get('course_id')
        tipo_evaluacion = data.get('tipo', 'Evaluación')
        peso = float(data.get('peso', 0.33))
        
        if not course_id:
            return jsonify({'success': False, 'error': 'Se requiere course_id'}), 400
        
        matriculas = get_matriculas_collection()
        curso_obj_id = string_to_objectid(course_id)
        
        successful = 0
        failed = 0
        errors = []
        
        for grade_entry in data['grades']:
            try:
                enrollment_id = grade_entry.get('enrollment_id')
                nota = float(grade_entry.get('nota', 0))
                comentarios = grade_entry.get('comentarios', '')
                
                if not enrollment_id:
                    failed += 1
                    errors.append({'error': 'enrollment_id requerido', 'entry': grade_entry})
                    continue
                
                enrollment_obj_id = string_to_objectid(enrollment_id)
                matricula = matriculas.find_one({'_id': enrollment_obj_id})
                
                if not matricula:
                    failed += 1
                    errors.append({'error': 'Matrícula no encontrada', 'enrollment_id': enrollment_id})
                    continue
                
                nueva_calificacion = {
                    'tipo': tipo_evaluacion,
                    'nota': nota,
                    'nota_maxima': 5.0,
                    'peso': peso,
                    'fecha_eval': datetime.utcnow(),
                    'comentarios': comentarios
                }
                
                matriculas.update_one(
                    {'_id': enrollment_obj_id},
                    {'$push': {'calificaciones': nueva_calificacion}}
                )
                
                successful += 1
                
            except Exception as e:
                failed += 1
                errors.append({'error': str(e), 'entry': grade_entry})
        
        registrar_auditoria(
            id_usuario=g.userinfo.get('sub'),
            accion='carga_masiva_calificaciones',
            entidad_afectada='matriculas',
            id_entidad=course_id,
            detalles=f"Carga masiva: {successful} exitosas, {failed} fallidas"
        )
        
        return jsonify({
            'success': True,
            'message': 'Carga masiva completada',
            'successful': successful,
            'failed': failed,
            'errors': errors if errors else None
        }), 200 if failed == 0 else 207
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/attendance', methods=['GET'])
@token_required('docente')
def get_attendance_by_course():
    """Obtener asistencia de un curso en una fecha específica"""
    try:
        course_id = request.args.get('course_id')
        fecha = request.args.get('fecha')  # Formato: YYYY-MM-DD
        
        if not course_id or not fecha:
            return jsonify({
                'success': False,
                'error': 'Se requieren course_id y fecha'
            }), 400
        
        # Convertir IDs
        curso_obj_id = string_to_objectid(course_id)
        if not curso_obj_id:
            return jsonify({'success': False, 'error': 'ID de curso inválido'}), 400
        
        # Convertir fecha string a datetime
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha inválido'}), 400
        
        asistencia = get_asistencia_collection()
        
        # Buscar registro de asistencia
        registro = asistencia.find_one({
            'id_curso': curso_obj_id,
            'fecha': fecha_obj
        })
        
        if registro:
            return jsonify({
                'success': True,
                'attendance': serialize_doc(registro)
            }), 200
        else:
            # Si no existe, devolver estructura vacía
            return jsonify({
                'success': True,
                'attendance': None,
                'message': 'No hay registro de asistencia para esta fecha'
            }), 200
        
    except Exception as e:
        print(f"❌ Error en get_attendance_by_course: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/attendance', methods=['POST'])
@token_required('docente')
def save_attendance():
    """Guardar o actualizar registro de asistencia"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400
        
        # Validar campos requeridos
        required_fields = ['course_id', 'fecha', 'registros']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # 🔧 CORRECCIÓN: Obtener email del token correctamente
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        print(f"🔍 Datos del token:")
        print(f"   Email: {teacher_email}")
        print(f"   Sub: {teacher_sub}")
        print(f"   UserInfo completo: {g.userinfo}")
        
        usuarios = get_usuarios_collection()
        
        # Buscar docente por email primero
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        # Si no se encuentra por email, intentar por keycloak_id
        if not docente:
            print(f"⚠️ No se encontró por email, intentando por keycloak_id...")
            docente = usuarios.find_one({
                'keycloak_id': teacher_sub,
                'rol': 'docente',
                'activo': True
            })
        
        # Si aún no se encuentra, intentar por _id (si el sub es un ObjectId válido)
        if not docente:
            print(f"⚠️ No se encontró por keycloak_id, intentando por _id...")
            teacher_obj_id = string_to_objectid(teacher_sub)
            if teacher_obj_id:
                docente = usuarios.find_one({
                    '_id': teacher_obj_id,
                    'rol': 'docente',
                    'activo': True
                })
        
        if not docente:
            print(f"❌ Docente no encontrado en la base de datos")
            print(f"   Email buscado: {teacher_email}")
            print(f"   Sub buscado: {teacher_sub}")
            return jsonify({
                'success': False,
                'error': 'Docente no encontrado en la base de datos'
            }), 404
        
        print(f"✅ Docente encontrado: {docente.get('nombres')} {docente.get('apellidos')}")
        
        # Convertir curso_id
        curso_obj_id = string_to_objectid(data['course_id'])
        if not curso_obj_id:
            return jsonify({'success': False, 'error': 'ID de curso inválido'}), 400
        
        # Verificar que el curso existe y pertenece al docente
        cursos = get_cursos_collection()
        curso = cursos.find_one({'_id': curso_obj_id})
        
        if not curso:
            return jsonify({'success': False, 'error': 'Curso no encontrado'}), 404
        
        if curso.get('id_docente') != docente['_id']:
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para registrar asistencia en este curso'
            }), 403
        
        # Convertir fecha
        try:
            fecha_obj = datetime.strptime(data['fecha'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha inválido'}), 400
        
        # Preparar registros de asistencia con información de estudiantes
        registros_procesados = []
        matriculas = get_matriculas_collection()
        
        for registro in data['registros']:
            estudiante_id = string_to_objectid(registro['id_estudiante'])
            if not estudiante_id:
                continue
            
            # Buscar información del estudiante desde la matrícula
            matricula = matriculas.find_one({
                'id_estudiante': estudiante_id,
                'id_curso': curso_obj_id,
                'estado': 'activo'
            })
            
            if matricula:
                registros_procesados.append({
                    'id_estudiante': estudiante_id,
                    'estudiante_info': matricula.get('estudiante_info', {}),
                    'estado': registro.get('estado', 'presente'),
                    'observaciones': registro.get('observaciones', '')
                })
        
        # Crear documento de asistencia
        asistencia = get_asistencia_collection()
        
        documento_asistencia = {
            'id_curso': curso_obj_id,
            'id_docente': docente['_id'],
            'fecha': fecha_obj,
            'periodo': data.get('periodo', curso.get('periodo', '1')),
            'registros': registros_procesados,
            'curso_info': {
                'nombre_curso': curso.get('nombre_curso', ''),
                'codigo_curso': curso.get('codigo_curso', ''),
                'grado': curso.get('grado', '')
            },
            'actualizado_en': Timestamp(int(datetime.utcnow().timestamp()), 0)
        }
        
        # Verificar si ya existe registro para esa fecha
        registro_existente = asistencia.find_one({
            'id_curso': curso_obj_id,
            'fecha': fecha_obj
        })
        
        if registro_existente:
            # Actualizar registro existente
            resultado = asistencia.update_one(
                {'_id': registro_existente['_id']},
                {'$set': documento_asistencia}
            )
            
            mensaje = 'Asistencia actualizada exitosamente'
            registro_id = str(registro_existente['_id'])
        else:
            # Crear nuevo registro
            documento_asistencia['creado_en'] = Timestamp(int(datetime.utcnow().timestamp()), 0)
            resultado = asistencia.insert_one(documento_asistencia)
            mensaje = 'Asistencia registrada exitosamente'
            registro_id = str(resultado.inserted_id)
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=docente['_id'],
            accion='registrar_asistencia',
            entidad_afectada='asistencia',
            id_entidad=registro_id,
            detalles=f"Asistencia registrada para {curso.get('nombre_curso')} - {data['fecha']}"
        )
        
        return jsonify({
            'success': True,
            'message': mensaje,
            'attendance_id': registro_id
        }), 201
        
    except Exception as e:
        print(f"❌ Error en save_attendance: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/attendance/statistics', methods=['GET'])
@token_required('docente')
def get_attendance_statistics():
    """Obtener estadísticas de asistencia de un curso"""
    try:
        course_id = request.args.get('course_id')
        periodo = request.args.get('periodo')
        
        if not course_id:
            return jsonify({'success': False, 'error': 'Se requiere course_id'}), 400
        
        curso_obj_id = string_to_objectid(course_id)
        if not curso_obj_id:
            return jsonify({'success': False, 'error': 'ID de curso inválido'}), 400
        
        asistencia = get_asistencia_collection()
        
        # Construir query
        query = {'id_curso': curso_obj_id}
        if periodo:
            query['periodo'] = periodo
        
        # Obtener todos los registros de asistencia del curso
        registros = list(asistencia.find(query).sort('fecha', -1))
        
        # Calcular estadísticas
        total_registros = len(registros)
        total_estudiantes = 0
        total_presentes = 0
        total_ausentes = 0
        total_tardes = 0
        
        # Estadísticas por estudiante
        estadisticas_estudiantes = {}
        
        for registro in registros:
            for item in registro.get('registros', []):
                estudiante_id = str(item['id_estudiante'])
                estado = item.get('estado', 'presente')
                
                if estudiante_id not in estadisticas_estudiantes:
                    estadisticas_estudiantes[estudiante_id] = {
                        'estudiante_info': item.get('estudiante_info', {}),
                        'total_clases': 0,
                        'presentes': 0,
                        'ausentes': 0,
                        'tardes': 0,
                        'excusas': 0
                    }
                
                estadisticas_estudiantes[estudiante_id]['total_clases'] += 1
                
                if estado == 'presente':
                    estadisticas_estudiantes[estudiante_id]['presentes'] += 1
                    total_presentes += 1
                elif estado == 'ausente':
                    estadisticas_estudiantes[estudiante_id]['ausentes'] += 1
                    total_ausentes += 1
                elif estado == 'tarde':
                    estadisticas_estudiantes[estudiante_id]['tardes'] += 1
                    total_tardes += 1
                elif estado == 'excusa':
                    estadisticas_estudiantes[estudiante_id]['excusas'] += 1
        
        # Calcular porcentajes por estudiante
        estudiantes_stats = []
        for est_id, stats in estadisticas_estudiantes.items():
            total_clases = stats['total_clases']
            porcentaje_asistencia = round((stats['presentes'] / total_clases * 100), 2) if total_clases > 0 else 0
            
            estudiantes_stats.append({
                'estudiante_id': est_id,
                'estudiante_info': stats['estudiante_info'],
                'total_clases': total_clases,
                'presentes': stats['presentes'],
                'ausentes': stats['ausentes'],
                'tardes': stats['tardes'],
                'excusas': stats['excusas'],
                'porcentaje_asistencia': porcentaje_asistencia
            })
        
        # Ordenar por porcentaje de asistencia descendente
        estudiantes_stats.sort(key=lambda x: x['porcentaje_asistencia'], reverse=True)
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_registros': total_registros,
                'total_presentes': total_presentes,
                'total_ausentes': total_ausentes,
                'total_tardes': total_tardes,
                'estudiantes': estudiantes_stats
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error en get_attendance_statistics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/teacher/observations', methods=['GET'])
@token_required('docente')
def get_teacher_observations():
    """Obtener observaciones registradas por el docente"""
    try:
        # Obtener filtros opcionales
        curso_id = request.args.get('course_id')
        tipo = request.args.get('tipo')  # positiva, negativa, neutral
        categoria = request.args.get('categoria')
        estudiante_id = request.args.get('student_id')
        
        # Obtener ID del docente desde el token
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        usuarios = get_usuarios_collection()
        
        # Buscar docente
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        if not docente:
            teacher_obj_id = string_to_objectid(teacher_sub)
            if teacher_obj_id:
                docente = usuarios.find_one({
                    '_id': teacher_obj_id,
                    'rol': 'docente',
                    'activo': True
                })
        
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        # Construir query
        query = {'id_docente': docente['_id']}
        
        if curso_id:
            curso_obj_id = string_to_objectid(curso_id)
            if curso_obj_id:
                query['id_curso'] = curso_obj_id
        
        if tipo and tipo != 'todas':
            query['tipo'] = tipo.lower()
        
        if categoria:
            query['categoria'] = categoria
        
        if estudiante_id:
            estudiante_obj_id = string_to_objectid(estudiante_id)
            if estudiante_obj_id:
                query['id_estudiante'] = estudiante_obj_id
        
        observaciones = get_observaciones_collection()
        
        # Obtener observaciones ordenadas por fecha descendente
        resultado = list(observaciones.find(query).sort('fecha', -1))
        
        # Calcular estadísticas
        total = len(resultado)
        positivas = len([o for o in resultado if o.get('tipo') == 'positiva'])
        negativas = len([o for o in resultado if o.get('tipo') == 'negativa'])
        neutrales = len([o for o in resultado if o.get('tipo') == 'neutral'])
        
        return jsonify({
            'success': True,
            'observations': [serialize_doc(o) for o in resultado],
            'statistics': {
                'total': total,
                'positivas': positivas,
                'negativas': negativas,
                'neutrales': neutrales
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error en get_teacher_observations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/teacher/observations', methods=['POST'])
@token_required('docente')
def create_observation():
    """Crear una nueva observación"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400
        
        # Validar campos requeridos
        required_fields = ['student_id', 'course_id', 'tipo', 'descripcion']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Obtener ID del docente desde el token
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        usuarios = get_usuarios_collection()
        
        # Buscar docente
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        if not docente:
            teacher_obj_id = string_to_objectid(teacher_sub)
            if teacher_obj_id:
                docente = usuarios.find_one({
                    '_id': teacher_obj_id,
                    'rol': 'docente',
                    'activo': True
                })
        
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        # Convertir IDs
        estudiante_id = string_to_objectid(data['student_id'])
        curso_id = string_to_objectid(data['course_id'])
        
        if not estudiante_id or not curso_id:
            return jsonify({'success': False, 'error': 'IDs inválidos'}), 400
        
        # Verificar que el estudiante existe
        estudiante = usuarios.find_one({'_id': estudiante_id, 'rol': 'estudiante'})
        if not estudiante:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
        
        # Verificar que el curso existe y pertenece al docente
        cursos = get_cursos_collection()
        curso = cursos.find_one({'_id': curso_id})
        
        if not curso:
            return jsonify({'success': False, 'error': 'Curso no encontrado'}), 404
        
        if curso.get('id_docente') != docente['_id']:
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para registrar observaciones en este curso'
            }), 403
        
        # Validar tipo
        tipo = data['tipo'].lower()
        if tipo not in ['positiva', 'negativa', 'neutral']:
            return jsonify({'success': False, 'error': 'Tipo de observación inválido'}), 400
        
        # Crear documento de observación
        observaciones = get_observaciones_collection()
        
        nueva_observacion = {
            'id_estudiante': estudiante_id,
            'id_docente': docente['_id'],
            'id_curso': curso_id,
            'tipo': tipo,
            'descripcion': data['descripcion'],
            'fecha': datetime.utcnow(),
            'seguimiento': data.get('seguimiento', ''),
            'categoria': data.get('categoria', 'otra'),
            'gravedad': data.get('gravedad', 'leve') if tipo == 'negativa' else None,
            'notificado_acudiente': data.get('notificado_acudiente', False),
            'fecha_notificacion': datetime.utcnow() if data.get('notificado_acudiente') else None,
            'estudiante_info': {
                'nombres': estudiante.get('nombres', ''),
                'apellidos': estudiante.get('apellidos', ''),
                'codigo_est': estudiante.get('codigo_est', '')
            },
            'docente_info': {
                'nombres': docente.get('nombres', ''),
                'apellidos': docente.get('apellidos', ''),
                'especialidad': docente.get('especialidad', '')
            },
            'curso_info': {
                'nombre_curso': curso.get('nombre_curso', ''),
                'codigo_curso': curso.get('codigo_curso', ''),
                'grado': curso.get('grado', '')
            },
            'archivos_adjuntos': data.get('archivos_adjuntos', []),
            'creado_en': Timestamp(int(datetime.utcnow().timestamp()), 0),
            'actualizado_en': Timestamp(int(datetime.utcnow().timestamp()), 0)
        }
        
        # Insertar observación
        resultado = observaciones.insert_one(nueva_observacion)
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=docente['_id'],
            accion='crear_observacion',
            entidad_afectada='observaciones',
            id_entidad=str(resultado.inserted_id),
            detalles=f"Observación {tipo} creada para {estudiante.get('nombres')} {estudiante.get('apellidos')}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Observación creada exitosamente',
            'observation_id': str(resultado.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"❌ Error en create_observation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/teacher/observations/<observation_id>', methods=['PUT'])
@token_required('docente')
def update_observation(observation_id):
    """Actualizar una observación existente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400
        
        # Convertir observation_id
        obs_obj_id = string_to_objectid(observation_id)
        if not obs_obj_id:
            return jsonify({'success': False, 'error': 'ID de observación inválido'}), 400
        
        # Obtener ID del docente desde el token
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        usuarios = get_usuarios_collection()
        
        # Buscar docente
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        if not docente:
            teacher_obj_id = string_to_objectid(teacher_sub)
            if teacher_obj_id:
                docente = usuarios.find_one({
                    '_id': teacher_obj_id,
                    'rol': 'docente',
                    'activo': True
                })
        
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        observaciones = get_observaciones_collection()
        
        # Verificar que la observación existe y pertenece al docente
        observacion = observaciones.find_one({'_id': obs_obj_id})
        
        if not observacion:
            return jsonify({'success': False, 'error': 'Observación no encontrada'}), 404
        
        if observacion.get('id_docente') != docente['_id']:
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para editar esta observación'
            }), 403
        
        # Preparar actualización
        actualizacion = {
            'actualizado_en': Timestamp(int(datetime.utcnow().timestamp()), 0)
        }
        
        # Campos actualizables
        campos_permitidos = ['descripcion', 'seguimiento', 'tipo', 'categoria', 'gravedad', 
                            'notificado_acudiente']
        
        for campo in campos_permitidos:
            if campo in data:
                actualizacion[campo] = data[campo]
        
        # Si se marca como notificado, agregar fecha
        if data.get('notificado_acudiente') and not observacion.get('fecha_notificacion'):
            actualizacion['fecha_notificacion'] = datetime.utcnow()
        
        # Actualizar observación
        observaciones.update_one(
            {'_id': obs_obj_id},
            {'$set': actualizacion}
        )
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=docente['_id'],
            accion='actualizar_observacion',
            entidad_afectada='observaciones',
            id_entidad=observation_id,
            detalles=f"Observación actualizada"
        )
        
        # Obtener observación actualizada
        obs_actualizada = observaciones.find_one({'_id': obs_obj_id})
        
        return jsonify({
            'success': True,
            'message': 'Observación actualizada exitosamente',
            'observation': serialize_doc(obs_actualizada)
        }), 200
        
    except Exception as e:
        print(f"❌ Error en update_observation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/teacher/observations/<observation_id>', methods=['DELETE'])
@token_required('docente')
def delete_observation(observation_id):
    """Eliminar una observación"""
    try:
        # Convertir observation_id
        obs_obj_id = string_to_objectid(observation_id)
        if not obs_obj_id:
            return jsonify({'success': False, 'error': 'ID de observación inválido'}), 400
        
        # Obtener ID del docente desde el token
        teacher_email = g.userinfo.get('email') or g.userinfo.get('preferred_username')
        teacher_sub = g.userinfo.get('sub')
        
        usuarios = get_usuarios_collection()
        
        # Buscar docente
        docente = usuarios.find_one({
            'correo': teacher_email,
            'rol': 'docente',
            'activo': True
        })
        
        if not docente:
            teacher_obj_id = string_to_objectid(teacher_sub)
            if teacher_obj_id:
                docente = usuarios.find_one({
                    '_id': teacher_obj_id,
                    'rol': 'docente',
                    'activo': True
                })
        
        if not docente:
            return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
        
        observaciones = get_observaciones_collection()
        
        # Verificar que la observación existe y pertenece al docente
        observacion = observaciones.find_one({'_id': obs_obj_id})
        
        if not observacion:
            return jsonify({'success': False, 'error': 'Observación no encontrada'}), 404
        
        if observacion.get('id_docente') != docente['_id']:
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para eliminar esta observación'
            }), 403
        
        # Eliminar observación
        observaciones.delete_one({'_id': obs_obj_id})
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=docente['_id'],
            accion='eliminar_observacion',
            entidad_afectada='observaciones',
            id_entidad=observation_id,
            detalles=f"Observación eliminada"
        )
        
        return jsonify({
            'success': True,
            'message': 'Observación eliminada exitosamente'
        }), 200
        
    except Exception as e:
        print(f"❌ Error en delete_observation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/teacher/observations/student/<student_id>', methods=['GET'])
@token_required('docente')
def get_student_observations(student_id):
    """Obtener historial de observaciones de un estudiante específico"""
    try:
        # Convertir student_id
        estudiante_obj_id = string_to_objectid(student_id)
        if not estudiante_obj_id:
            return jsonify({'success': False, 'error': 'ID de estudiante inválido'}), 400
        
        observaciones = get_observaciones_collection()
        
        # Obtener observaciones del estudiante ordenadas por fecha
        resultado = list(observaciones.find(
            {'id_estudiante': estudiante_obj_id}
        ).sort('fecha', -1))
        
        # Calcular estadísticas del estudiante
        total = len(resultado)
        positivas = len([o for o in resultado if o.get('tipo') == 'positiva'])
        negativas = len([o for o in resultado if o.get('tipo') == 'negativa'])
        neutrales = len([o for o in resultado if o.get('tipo') == 'neutral'])
        
        return jsonify({
            'success': True,
            'observations': [serialize_doc(o) for o in resultado],
            'statistics': {
                'total': total,
                'positivas': positivas,
                'negativas': negativas,
                'neutrales': neutrales
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error en get_student_observations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)