from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

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
        'service': 'Students Service',
        'version': '2.0.0',
        'database': 'MongoDB',
        'endpoints': {
            'get_all': 'GET /students',
            'get_one': 'GET /students/{id}',
            'create': 'POST /students',
            'update': 'PUT /students/{id}',
            'delete': 'DELETE /students/{id}'
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
        grado = request.args.get('grade_level')
        status = request.args.get('status')
        
        # Construir query
        query = {'rol': 'estudiante'}
        
        if status:
            query['activo'] = (status == 'active')
        
        # Buscar estudiantes
        estudiantes = list(usuarios.find(query))
        
        # Serializar documentos
        estudiantes_serializados = serialize_doc(estudiantes)
        
        return jsonify({
            'students': estudiantes_serializados,
            'count': len(estudiantes_serializados)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Obtener un estudiante por ID"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'error': 'Invalid student ID'}), 400
        
        # Buscar estudiante
        estudiante = usuarios.find_one({'_id': obj_id, 'rol': 'estudiante'})
        
        if not estudiante:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify({'student': serialize_doc(estudiante)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students', methods=['POST'])
def create_student():
    """Crear un nuevo estudiante"""
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
        
        # Crear documento de estudiante
        estudiante = {
            'correo': data['correo'],
            'rol': 'estudiante',
            'nombres': data['nombres'],
            'apellidos': data['apellidos'],
            'codigo_est': data.get('codigo_est', ''),
            'telefono': data.get('telefono', ''),
            'fecha_nacimiento': datetime.fromisoformat(data['fecha_nacimiento']) if data.get('fecha_nacimiento') else None,
            'direccion': data.get('direccion', ''),
            'nombre_acudiente': data.get('nombre_acudiente', ''),
            'telefono_acudiente': data.get('telefono_acudiente', ''),
            'activo': data.get('activo', True),
            'creado_en': datetime.utcnow()
        }
        
        # Insertar en MongoDB
        result = usuarios.insert_one(estudiante)
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='crear_estudiante',
            entidad_afectada='usuarios',
            id_entidad=str(result.inserted_id),
            detalles=f"Estudiante creado: {data['nombres']} {data['apellidos']}"
        )
        
        estudiante['_id'] = result.inserted_id
        
        return jsonify({
            'message': 'Student created successfully',
            'student': serialize_doc(estudiante)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Actualizar un estudiante"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'error': 'Invalid student ID'}), 400
        
        # Verificar que el estudiante existe
        estudiante = usuarios.find_one({'_id': obj_id, 'rol': 'estudiante'})
        if not estudiante:
            return jsonify({'error': 'Student not found'}), 404
        
        # Verificar email único (si se está actualizando)
        if 'correo' in data and data['correo'] != estudiante.get('correo'):
            if usuarios.find_one({'correo': data['correo']}):
                return jsonify({'error': 'Email already exists'}), 400
        
        # Preparar actualización
        update_data = {}
        updatable_fields = ['nombres', 'apellidos', 'correo', 'telefono', 'codigo_est', 
                          'direccion', 'nombre_acudiente', 'telefono_acudiente', 'activo']
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Manejar fecha de nacimiento
        if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
            update_data['fecha_nacimiento'] = datetime.fromisoformat(data['fecha_nacimiento'])
        
        # Actualizar en MongoDB
        result = usuarios.update_one(
            {'_id': obj_id},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            # Registrar auditoría
            registrar_auditoria(
                id_usuario=None,
                accion='actualizar_estudiante',
                entidad_afectada='usuarios',
                id_entidad=student_id,
                detalles=f"Estudiante actualizado: {update_data.get('nombres', '')} {update_data.get('apellidos', '')}"
            )
        
        # Obtener estudiante actualizado
        estudiante_actualizado = usuarios.find_one({'_id': obj_id})
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': serialize_doc(estudiante_actualizado)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Eliminar (desactivar) un estudiante"""
    try:
        usuarios = get_usuarios_collection()
        
        # Convertir ID a ObjectId
        obj_id = string_to_objectid(student_id)
        if not obj_id:
            return jsonify({'error': 'Invalid student ID'}), 400
        
        # Buscar estudiante
        estudiante = usuarios.find_one({'_id': obj_id, 'rol': 'estudiante'})
        if not estudiante:
            return jsonify({'error': 'Student not found'}), 404
        
        # Desactivar en lugar de eliminar
        result = usuarios.update_one(
            {'_id': obj_id},
            {'$set': {'activo': False}}
        )
        
        # Registrar auditoría
        registrar_auditoria(
            id_usuario=None,
            accion='desactivar_estudiante',
            entidad_afectada='usuarios',
            id_entidad=student_id,
            detalles=f"Estudiante desactivado: {estudiante.get('nombres')} {estudiante.get('apellidos')}"
        )
        
        return jsonify({
            'message': 'Student deactivated successfully',
            'deleted_student': serialize_doc(estudiante)
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


@app.route('/student/grades/<student_id>')
def student_grades(student_id):
    """Obtener calificaciones de un estudiante"""
    try:
        matriculas = get_matriculas_collection()
        obj_id = string_to_objectid(student_id)
        
        if not obj_id:
            return jsonify({'error': 'Invalid student ID'}), 400
        
        # Buscar matrículas activas del estudiante
        matriculas_estudiante = list(matriculas.find({
            'id_estudiante': obj_id,
            'estado': 'activo'
        }))
        
        # Extraer calificaciones
        todas_calificaciones = []
        for matricula in matriculas_estudiante:
            curso_info = matricula.get('curso_info', {})
            calificaciones = matricula.get('calificaciones', [])
            
            for calif in calificaciones:
                todas_calificaciones.append({
                    'subject': curso_info.get('nombre_curso', 'N/A'),
                    'tipo': calif.get('tipo', ''),
                    'grade': calif.get('nota', 0),
                    'nota_maxima': calif.get('nota_maxima', 5),
                    'date': calif.get('fecha_eval', '').isoformat() if calif.get('fecha_eval') else ''
                })
        
        # Calcular promedio
        if todas_calificaciones:
            total_notas = sum(c['grade'] for c in todas_calificaciones)
            average = round(total_notas / len(todas_calificaciones), 2)
        else:
            average = 0
        
        return jsonify({
            'recent': todas_calificaciones[:10],  # Últimas 10
            'average': average
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/student/notifications')
def student_notifications():
    """Obtener notificaciones del estudiante (mock por ahora)"""
    notes = [
        {'id': 'n1', 'title': 'Boletín del 3er periodo disponible', 'type': 'info'},
        {'id': 'n2', 'title': 'Entrega de proyecto de Ciencias mañana', 'type': 'warning'},
        {'id': 'n3', 'title': 'Reunión de padres el viernes 22', 'type': 'info'}
    ]
    return jsonify({'notifications': notes}), 200


@app.route('/student/schedule-today')
def student_schedule_today():
    """Obtener horario del día (mock por ahora)"""
    schedule = [
        {'time': '7:00 - 7:45', 'subject': 'Matemáticas', 'location': 'A101', 'teacher': 'Prof. García'},
        {'time': '7:45 - 8:30', 'subject': 'Español', 'location': 'A102', 'teacher': 'Prof. López'},
        {'time': '8:30 - 9:15', 'subject': 'Ciencias', 'location': 'Lab 1', 'teacher': 'Prof. Martín'},
        {'time': '10:00 - 10:45', 'subject': 'Inglés', 'location': 'A103', 'teacher': 'Prof. Smith'},
        {'time': '10:45 - 11:30', 'subject': 'Ed. Física', 'location': 'Polideportivo', 'teacher': 'Prof. Ruiz'}
    ]
    return jsonify({'date': datetime.utcnow().strftime('%A, %d de %B de %Y'), 'events': schedule}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)