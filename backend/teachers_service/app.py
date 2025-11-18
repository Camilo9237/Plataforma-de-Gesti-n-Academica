from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Agregar el path del backend para importar db_config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_config import (
    get_usuarios_collection,
    get_cursos_collection,
    serialize_doc,
    string_to_objectid,
    registrar_auditoria
)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:4200", "https://your-frontend-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


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
            query['activo'] = (status == 'active')
        
        if especialidad:
            query['especialidad'] = {'$regex': especialidad, '$options': 'i'}
        
        # Buscar docentes
        docentes = list(usuarios.find(query))
        
        # Serializar documentos
        docentes_serializados = serialize_doc(docentes)
        
        return jsonify({
            'teachers': docentes_serializados,
            'count': len(docentes_serializados)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    """Obtener un profesor por ID"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(teacher_id)
        if not obj_id:
            return jsonify({'error': 'Invalid teacher ID'}), 400
        
        # Buscar docente
        docente = usuarios.find_one({'_id': obj_id, 'rol': 'docente'})
        
        if not docente:
            return jsonify({'error': 'Teacher not found'}), 404
        
        return jsonify({'teacher': serialize_doc(docente)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teachers', methods=['POST'])
def create_teacher():
    """Crear un nuevo profesor"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validar campos requeridos
        required_fields = ['correo', 'nombres', 'apellidos']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        usuarios = get_usuarios_collection()
        
        # Verificar si el correo ya existe
        if usuarios.find_one({'correo': data['correo']}):
            return jsonify({'error': 'Email already exists'}), 400
        
        # Crear documento de docente
        docente = {
            'correo': data['correo'],
            'rol': 'docente',
            'nombres': data['nombres'],
            'apellidos': data['apellidos'],
            'codigo_empleado': data.get('codigo_empleado', ''),
            'telefono': data.get('telefono', ''),
            'especialidad': data.get('especialidad', ''),
            'fecha_ingreso': datetime.fromisoformat(data['fecha_ingreso']) if data.get('fecha_ingreso') else datetime.utcnow(),
            'activo': data.get('activo', True),
            'creado_en': datetime.utcnow()
        }
        
        # Insertar en MongoDB
        result = usuarios.insert_one(docente)
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='crear_docente',
            entidad_afectada='usuarios',
            id_entidad=str(result.inserted_id),
            detalles=f"Docente creado: {data['nombres']} {data['apellidos']}"
        )
        
        docente['_id'] = result.inserted_id
        
        return jsonify({
            'message': 'Teacher created successfully',
            'teacher': serialize_doc(docente)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    """Actualizar un profesor"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(teacher_id)
        if not obj_id:
            return jsonify({'error': 'Invalid teacher ID'}), 400
        
        # Verificar que el docente existe
        docente = usuarios.find_one({'_id': obj_id, 'rol': 'docente'})
        if not docente:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Verificar email único (si se está actualizando)
        if 'correo' in data and data['correo'] != docente.get('correo'):
            if usuarios.find_one({'correo': data['correo']}):
                return jsonify({'error': 'Email already exists'}), 400
        
        # Preparar actualización
        update_data = {}
        updatable_fields = ['nombres', 'apellidos', 'correo', 'telefono', 'codigo_empleado',
                          'especialidad', 'activo']
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Manejar fecha de ingreso
        if 'fecha_ingreso' in data and data['fecha_ingreso']:
            update_data['fecha_ingreso'] = datetime.fromisoformat(data['fecha_ingreso'])
        
        # Actualizar en MongoDB
        result = usuarios.update_one(
            {'_id': obj_id},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            # Registrar auditoría
            registrar_auditoria(
                id_usuario=None,
                accion='actualizar_docente',
                entidad_afectada='usuarios',
                id_entidad=teacher_id,
                detalles=f"Docente actualizado: {update_data.get('nombres', '')} {update_data.get('apellidos', '')}"
            )
        
        # Obtener docente actualizado
        docente_actualizado = usuarios.find_one({'_id': obj_id})
        
        return jsonify({
            'message': 'Teacher updated successfully',
            'teacher': serialize_doc(docente_actualizado)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Eliminar (desactivar) un profesor"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(teacher_id)
        if not obj_id:
            return jsonify({'error': 'Invalid teacher ID'}), 400
        
        # Buscar docente
        docente = usuarios.find_one({'_id': obj_id, 'rol': 'docente'})
        if not docente:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Desactivar en lugar de eliminar
        result = usuarios.update_one(
            {'_id': obj_id},
            {'$set': {'activo': False}}
        )
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='desactivar_docente',
            entidad_afectada='usuarios',
            id_entidad=teacher_id,
            detalles=f"Docente desactivado: {docente.get('nombres')} {docente.get('apellidos')}"
        )
        
        return jsonify({
            'message': 'Teacher deactivated successfully',
            'deleted_teacher': serialize_doc(docente)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/subjects', methods=['GET'])
def get_subjects():
    """Obtener lista de especialidades disponibles"""
    try:
        usuarios = get_usuarios_collection()
        
        # Obtener especialidades únicas
        especialidades = usuarios.distinct('especialidad', {'rol': 'docente', 'especialidad': {'$ne': None, '$ne': ''}})
        especialidades = sorted([e for e in especialidades if e])
        
        return jsonify({
            'subjects': especialidades,
            'count': len(especialidades)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/teacher/groups/<teacher_id>')
def teacher_groups(teacher_id):
    """Obtener grupos asignados a un docente"""
    try:
        cursos = get_cursos_collection()
        obj_id = string_to_objectid(teacher_id)
        
        if not obj_id:
            return jsonify({'error': 'Invalid teacher ID'}), 400
        
        # Buscar cursos del docente
        cursos_docente = list(cursos.find({'id_docente': obj_id, 'activo': True}))
        
        grupos = []
        for curso in cursos_docente:
            grupos.append({
                'id': str(curso['_id']),
                'name': curso.get('nombre_curso', ''),
                'code': curso.get('codigo_curso', ''),
                'grade': curso.get('grado', ''),
                'periodo': curso.get('periodo', '')
            })
        
        return jsonify({'groups': grupos}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/teacher/pending-grades')
def teacher_pending_grades():
    """Calificaciones pendientes (mock por ahora)"""
    pending = [
        {'course': "Matemáticas 10°A", 'pending': 12},
        {'course': "Física 11°B", 'pending': 8},
        {'course': "Matemáticas 9°C", 'pending': 5}
    ]
    return jsonify({'pending': pending}), 200


@app.route('/teacher/overview')
def teacher_overview():
    """Resumen del docente (mock por ahora)"""
    overview = {
        'groups_count': 3,
        'pending_grades': 25,
        'next_event': 'Entrega de notas el viernes'
    }
    return jsonify({'overview': overview}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)