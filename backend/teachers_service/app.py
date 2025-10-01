from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:4200", "https://your-frontend-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Base de datos en memoria para profesores
teachers_db = [
    {
        'id': '1',
        'name': 'Dr. María López',
        'email': 'maria.lopez@colegio.edu',
        'phone': '555-1001',
        'subject': 'Matemáticas',
        'qualification': 'Doctorado en Matemáticas',
        'experience_years': 12,
        'hire_date': '2018-02-15',
        'status': 'active',
        'salary': 4500000,
        'address': 'Calle Principal #123',
        'department': 'Ciencias Exactas',
        'created_at': '2024-01-10T08:00:00Z',
        'updated_at': '2024-01-10T08:00:00Z'
    },
    {
        'id': '2',
        'name': 'Lic. Carlos Rodríguez',
        'email': 'carlos.rodriguez@colegio.edu',
        'phone': '555-1002',
        'subject': 'Ciencias Naturales',
        'qualification': 'Licenciatura en Biología',
        'experience_years': 8,
        'hire_date': '2020-08-20',
        'status': 'active',
        'salary': 3800000,
        'address': 'Avenida Central #456',
        'department': 'Ciencias Naturales',
        'created_at': '2024-01-11T09:30:00Z',
        'updated_at': '2024-01-11T09:30:00Z'
    },
    {
        'id': '3',
        'name': 'Prof. Ana Martín',
        'email': 'ana.martin@colegio.edu',
        'phone': '555-1003',
        'subject': 'Literatura',
        'qualification': 'Maestría en Literatura Hispanoamericana',
        'experience_years': 15,
        'hire_date': '2015-03-10',
        'status': 'active',
        'salary': 4200000,
        'address': 'Calle Literaria #789',
        'department': 'Humanidades',
        'created_at': '2024-01-12T11:15:00Z',
        'updated_at': '2024-01-12T11:15:00Z'
    }
]

@app.route('/')
def home():
    return jsonify({
        'service': 'Teachers Service',
        'version': '1.0.0',
        'endpoints': {
            'get_all': 'GET /teachers',
            'get_one': 'GET /teachers/{id}',
            'create': 'POST /teachers',
            'update': 'PUT /teachers/{id}',
            'delete': 'DELETE /teachers/{id}',
            'by_subject': 'GET /teachers?subject={subject}',
            'by_department': 'GET /teachers?department={department}'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'teachers'})

@app.route('/teachers', methods=['GET'])
def get_teachers():
    """Obtener todos los profesores"""
    try:
        # Filtros opcionales
        subject = request.args.get('subject')
        department = request.args.get('department')
        status = request.args.get('status', 'active')
        
        filtered_teachers = teachers_db
        
        if subject:
            filtered_teachers = [t for t in filtered_teachers if t.get('subject', '').lower() == subject.lower()]
        
        if department:
            filtered_teachers = [t for t in filtered_teachers if t.get('department', '').lower() == department.lower()]
        
        if status:
            filtered_teachers = [t for t in filtered_teachers if t.get('status') == status]
        
        return jsonify({
            'teachers': filtered_teachers,
            'count': len(filtered_teachers),
            'total': len(teachers_db)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    """Obtener un profesor por ID"""
    try:
        teacher = next((t for t in teachers_db if t['id'] == teacher_id), None)
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        return jsonify({'teacher': teacher}), 200
        
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
        required_fields = ['name', 'email', 'phone', 'subject']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verificar si el email ya existe
        if any(t['email'] == data['email'] for t in teachers_db):
            return jsonify({'error': 'Email already exists'}), 400
        
        # Crear profesor
        new_id = str(len(teachers_db) + 1)
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        teacher = {
            'id': new_id,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'subject': data['subject'],
            'qualification': data.get('qualification', ''),
            'experience_years': data.get('experience_years', 0),
            'hire_date': data.get('hire_date', timestamp.split('T')[0]),
            'status': data.get('status', 'active'),
            'salary': data.get('salary', 0),
            'address': data.get('address', ''),
            'department': data.get('department', ''),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        teachers_db.append(teacher)
        
        return jsonify({
            'message': 'Teacher created successfully',
            'teacher': teacher
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
        
        # Buscar profesor
        teacher_index = next((i for i, t in enumerate(teachers_db) if t['id'] == teacher_id), None)
        
        if teacher_index is None:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Verificar email único (si se está actualizando)
        if 'email' in data:
            existing_email = any(t['email'] == data['email'] and t['id'] != teacher_id for t in teachers_db)
            if existing_email:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Actualizar campos
        updatable_fields = ['name', 'email', 'phone', 'subject', 'qualification', 'experience_years', 'hire_date', 'status', 'salary', 'address', 'department']
        
        for field in updatable_fields:
            if field in data:
                teachers_db[teacher_index][field] = data[field]
        
        teachers_db[teacher_index]['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return jsonify({
            'message': 'Teacher updated successfully',
            'teacher': teachers_db[teacher_index]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Eliminar un profesor"""
    try:
        teacher_index = next((i for i, t in enumerate(teachers_db) if t['id'] == teacher_id), None)
        
        if teacher_index is None:
            return jsonify({'error': 'Teacher not found'}), 404
        
        deleted_teacher = teachers_db.pop(teacher_index)
        
        return jsonify({
            'message': 'Teacher deleted successfully',
            'deleted_teacher': deleted_teacher
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/subjects', methods=['GET'])
def get_subjects():
    """Obtener lista de materias disponibles"""
    try:
        subjects = list(set(t.get('subject', '') for t in teachers_db if t.get('subject')))
        subjects.sort()
        
        return jsonify({
            'subjects': subjects,
            'count': len(subjects)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/departments', methods=['GET'])
def get_departments():
    """Obtener lista de departamentos disponibles"""
    try:
        departments = list(set(t.get('department', '') for t in teachers_db if t.get('department')))
        departments.sort()
        
        return jsonify({
            'departments': departments,
            'count': len(departments)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)