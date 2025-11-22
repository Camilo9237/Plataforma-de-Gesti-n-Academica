from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime
from bson.timestamp import Timestamp
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_config import (
    get_usuarios_collection,
    get_cursos_collection,
    get_matriculas_collection,
    serialize_doc,
    string_to_objectid,
    registrar_auditoria,
    get_groups_collection,
    get_horarios_collection
)

app = Flask(__name__)
app.secret_key = "GruposService"

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


# ==========================================
#   ENDPOINTS DE GRUPOS
# ==========================================

@app.route('/groups', methods=['GET'])
def get_all_groups():
    """Obtener todos los grupos"""
    try:
        grupos = get_groups_collection()
        
        # Filtros opcionales
        grado = request.args.get('grado')
        activo = request.args.get('activo')
        
        query = {}
        if grado:
            query['grado'] = grado
        if activo is not None:
            query['activo'] = activo.lower() == 'true'
        
        lista_grupos = list(grupos.find(query))
        
        # Agregar información de docente director
        usuarios = get_usuarios_collection()
        for grupo in lista_grupos:
            if grupo.get('director_grupo'):
                docente = usuarios.find_one({'_id': grupo['director_grupo']})
                if docente:
                    grupo['director_info'] = {
                        'nombres': docente.get('nombres'),
                        'apellidos': docente.get('apellidos'),
                        'especialidad': docente.get('especialidad')
                    }
        
        return jsonify({
            'success': True,
            'data': serialize_doc(lista_grupos),
            'count': len(lista_grupos)
        }), 200
        
    except Exception as e:
        print(f"❌ Error en get_all_groups: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/groups', methods=['POST'])
def create_group():
    """Crear un nuevo grupo"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required = ['nombre_grupo', 'grado', 'jornada', 'año_lectivo']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        grupos = get_groups_collection()
        
        # Verificar que no exista un grupo con el mismo nombre en el mismo año
        if grupos.find_one({
            'nombre_grupo': data['nombre_grupo'],
            'año_lectivo': data['año_lectivo']
        }):
            return jsonify({
                'success': False,
                'error': 'Ya existe un grupo con este nombre en el año lectivo'
            }), 400
        
        # Crear grupo
        nuevo_grupo = {
            'nombre_grupo': data['nombre_grupo'],
            'grado': data['grado'],
            'jornada': data['jornada'],
            'año_lectivo': data['año_lectivo'],
            'capacidad_max': data.get('capacidad_max', 40),
            'activo': data.get('activo', True),
            'creado_en': Timestamp(int(datetime.utcnow().timestamp()), 0)
        }
        
        if data.get('director_grupo'):
            nuevo_grupo['director_grupo'] = string_to_objectid(data['director_grupo'])
        
        resultado = grupos.insert_one(nuevo_grupo)
        
        registrar_auditoria(
            id_usuario=None,
            accion='crear_grupo',
            entidad_afectada='grupos',
            id_entidad=str(resultado.inserted_id),
            detalles=f"Grupo creado: {data['nombre_grupo']}"
        )
        
        grupo_creado = grupos.find_one({'_id': resultado.inserted_id})
        
        return jsonify({
            'success': True,
            'message': 'Grupo creado exitosamente',
            'data': serialize_doc(grupo_creado)
        }), 201
        
    except Exception as e:
        print(f"❌ Error en create_group: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/groups/<group_id>/students', methods=['GET'])
def get_group_students(group_id):
    """Obtener estudiantes de un grupo"""
    try:
        grupos = get_groups_collection()
        usuarios = get_usuarios_collection()
        
        # Verificar que el grupo existe
        obj_id = string_to_objectid(group_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        grupo = grupos.find_one({'_id': obj_id})
        if not grupo:
            return jsonify({'success': False, 'error': 'Grupo no encontrado'}), 404
        
        # Buscar estudiantes del grupo
        estudiantes = list(usuarios.find({
            'rol': 'estudiante',
            'grupo': grupo['nombre_grupo'],
            'activo': True
        }))
        
        return jsonify({
            'success': True,
            'grupo': grupo['nombre_grupo'],
            'estudiantes': serialize_doc(estudiantes),
            'count': len(estudiantes)
        }), 200
        
    except Exception as e:
        print(f"❌ Error en get_group_students: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/groups/<group_id>/assign-student', methods=['POST'])
def assign_student_to_group(group_id):
    """Asignar un estudiante a un grupo y matricularlo automáticamente en los cursos del grupo"""
    try:
        data = request.get_json()
        
        if 'student_id' not in data:
            return jsonify({'success': False, 'error': 'student_id requerido'}), 400
        
        grupos = get_groups_collection()
        usuarios = get_usuarios_collection()
        cursos = get_cursos_collection()
        matriculas = get_matriculas_collection()
        
        # Verificar grupo
        grupo_obj_id = string_to_objectid(group_id)
        if not grupo_obj_id:
            return jsonify({'success': False, 'error': 'ID de grupo inválido'}), 400
        
        grupo = grupos.find_one({'_id': grupo_obj_id})
        if not grupo:
            return jsonify({'success': False, 'error': 'Grupo no encontrado'}), 404
        
        # Verificar estudiante
        student_obj_id = string_to_objectid(data['student_id'])
        if not student_obj_id:
            return jsonify({'success': False, 'error': 'ID de estudiante inválido'}), 400
        
        estudiante = usuarios.find_one({
            '_id': student_obj_id,
            'rol': 'estudiante'
        })
        if not estudiante:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
        
        # Verificar capacidad del grupo
        estudiantes_actuales = usuarios.count_documents({
            'grupo': grupo['nombre_grupo'],
            'activo': True
        })
        
        if estudiantes_actuales >= grupo.get('capacidad_max', 40):
            return jsonify({
                'success': False,
                'error': 'El grupo ha alcanzado su capacidad máxima'
            }), 400
        
        # ✅ Asignar grupo al estudiante
        usuarios.update_one(
            {'_id': student_obj_id},
            {'$set': {'grupo': grupo['nombre_grupo']}}
        )
        
        # ✅ Buscar todos los cursos del grupo
        cursos_grupo = list(cursos.find({
            'grupo': grupo['nombre_grupo'],
            'activo': True
        }))
        
        # ✅ Matricular automáticamente en todos los cursos del grupo
        matriculas_creadas = 0
        for curso in cursos_grupo:
            # Verificar si ya está matriculado
            matricula_existente = matriculas.find_one({
                'id_estudiante': student_obj_id,
                'id_curso': curso['_id']
            })
            
            if not matricula_existente:
                # Crear matrícula
                nueva_matricula = {
                    'id_estudiante': student_obj_id,
                    'id_curso': curso['_id'],
                    'fecha_matricula': Timestamp(int(datetime.utcnow().timestamp()), 0),
                    'estado': 'activo',
                    'calificaciones': [],
                    'estudiante_info': {
                        'nombres': estudiante.get('nombres'),
                        'apellidos': estudiante.get('apellidos'),
                        'codigo_est': estudiante.get('codigo_est')
                    },
                    'curso_info': {
                        'nombre_curso': curso.get('nombre_curso'),
                        'codigo_curso': curso.get('codigo_curso'),
                        'grado': curso.get('grado'),
                        'periodo': curso.get('periodo')
                    }
                }
                
                matriculas.insert_one(nueva_matricula)
                matriculas_creadas += 1
        
        registrar_auditoria(
            id_usuario=None,
            accion='asignar_estudiante_grupo',
            entidad_afectada='usuarios',
            id_entidad=data['student_id'],
            detalles=f"Estudiante asignado a {grupo['nombre_grupo']} y matriculado en {matriculas_creadas} cursos"
        )
        
        return jsonify({
            'success': True,
            'message': f'Estudiante asignado al grupo {grupo["nombre_grupo"]}',
            'matriculas_creadas': matriculas_creadas
        }), 200
        
    except Exception as e:
        print(f"❌ Error en assign_student_to_group: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
#   ENDPOINTS DE HORARIOS
# ==========================================

@app.route('/groups/<group_id>/schedule', methods=['GET'])
def get_group_schedule(group_id):
    """Obtener horario de un grupo"""
    try:
        grupos = get_groups_collection()
        horarios = get_horarios_collection()
        
        # Verificar grupo
        obj_id = string_to_objectid(group_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        grupo = grupos.find_one({'_id': obj_id})
        if not grupo:
            return jsonify({'success': False, 'error': 'Grupo no encontrado'}), 404
        
        # Buscar horario
        horario = horarios.find_one({
            'grupo': grupo['nombre_grupo'],
            'año_lectivo': grupo.get('año_lectivo', '2025')
        })
        
        if not horario:
            return jsonify({
                'success': True,
                'grupo': grupo['nombre_grupo'],
                'horario': [],
                'message': 'No hay horario configurado para este grupo'
            }), 200
        
        return jsonify({
            'success': True,
            'data': serialize_doc(horario)
        }), 200
        
    except Exception as e:
        print(f"❌ Error en get_group_schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/groups/<group_id>/schedule', methods=['POST'])
def create_group_schedule(group_id):
    """Crear o actualizar horario de un grupo"""
    try:
        data = request.get_json()
        
        if 'horario' not in data or not isinstance(data['horario'], list):
            return jsonify({
                'success': False,
                'error': 'Se requiere un arreglo de bloques de horario'
            }), 400
        
        grupos = get_groups_collection()
        horarios = get_horarios_collection()
        
        # Verificar grupo
        obj_id = string_to_objectid(group_id)
        if not obj_id:
            return jsonify({'success': False, 'error': 'ID inválido'}), 400
        
        grupo = grupos.find_one({'_id': obj_id})
        if not grupo:
            return jsonify({'success': False, 'error': 'Grupo no encontrado'}), 404
        
        # Verificar si ya existe horario
        horario_existente = horarios.find_one({
            'grupo': grupo['nombre_grupo'],
            'año_lectivo': grupo.get('año_lectivo', '2025')
        })
        
        if horario_existente:
            # Actualizar
            horarios.update_one(
                {'_id': horario_existente['_id']},
                {
                    '$set': {
                        'horario': data['horario'],
                        'actualizado_en': Timestamp(int(datetime.utcnow().timestamp()), 0)
                    }
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Horario actualizado exitosamente'
            }), 200
        else:
            # Crear nuevo
            nuevo_horario = {
                'grupo': grupo['nombre_grupo'],
                'año_lectivo': grupo.get('año_lectivo', '2025'),
                'horario': data['horario'],
                'creado_en': Timestamp(int(datetime.utcnow().timestamp()), 0),
                'actualizado_en': Timestamp(int(datetime.utcnow().timestamp()), 0)
            }
            
            resultado = horarios.insert_one(nuevo_horario)
            
            registrar_auditoria(
                id_usuario=None,
                accion='crear_horario_grupo',
                entidad_afectada='horarios',
                id_entidad=str(resultado.inserted_id),
                detalles=f"Horario creado para {grupo['nombre_grupo']}"
            )
            
            return jsonify({
                'success': True,
                'message': 'Horario creado exitosamente'
            }), 201
        
    except Exception as e:
        print(f"❌ Error en create_group_schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'groups'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)