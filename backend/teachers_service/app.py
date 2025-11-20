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


# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)