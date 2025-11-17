from flask import Flask, request, jsonify
from flask_cors import CORS
import os

try:
    from keycloak import KeycloakOpenID
except Exception:
    KeycloakOpenID = None

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET', 'plataforma_secret')
CORS(app)

# Keycloak configuration (from env)
KEYCLOAK_SERVER = os.getenv('KEYCLOAK_SERVER_URL', 'http://localhost:8082')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', '01')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'plataformaInstitucional')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', '2m2KWH4lyYgh9CwoM1y2QI6bFrDjR3OV')

keycloak_openid = None
if KeycloakOpenID is not None:
    try:
        keycloak_openid = KeycloakOpenID(
            server_url=KEYCLOAK_SERVER,
            client_id=KEYCLOAK_CLIENT_ID,
            realm_name=KEYCLOAK_REALM,
            client_secret_key=KEYCLOAK_CLIENT_SECRET
        )
    except Exception:
        keycloak_openid = None


@app.route('/')
def home():
    return jsonify({
        'service': 'Login Service',
        'version': '1.0.0',
        'endpoints': {
            'login': 'POST /login',
            'logout': 'GET /logout',
            'health': 'GET /health'
        }
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'login'})


@app.route('/logout')
def logout():
    return jsonify({'message': 'Sesión cerrada'}), 200


@app.route('/login', methods=['POST'])
def login():
    """Login: si Keycloak está configurado usa Keycloak, si no, usa autenticación mock para desarrollo."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Faltan credenciales'}), 400

    # Prefer Keycloak if available
    if keycloak_openid is not None:
        try:
            token = keycloak_openid.token(username, password)
            access = token.get('access_token')
            # intentar decodificar token para obtener roles
            try:
                token_info = keycloak_openid.decode_token(access)
            except Exception:
                token_info = {}

            # determinar rol preferente
            role = None
            realm_roles = token_info.get('realm_access', {}).get('roles', []) if token_info else []
            if 'administrador' in realm_roles:
                role = 'administrador'
            elif 'docente' in realm_roles:
                role = 'docente'
            elif 'estudiante' in realm_roles:
                role = 'estudiante'

            # revisar roles por cliente
            if not role:
                for client_id, info in token_info.get('resource_access', {}).items() if token_info else []:
                    client_roles = info.get('roles', [])
                    if 'administrador' in client_roles:
                        role = 'administrador'
                        break
                    if 'docente' in client_roles:
                        role = 'docente'
                        break
                    if 'estudiante' in client_roles:
                        role = 'estudiante'
                        break

            # fallback si no se detecta
            if not role:
                role = 'estudiante'

            return jsonify({
                'access_token': access,
                'refresh_token': token.get('refresh_token'),
                'expires_in': token.get('expires_in'),
                'token_type': token.get('token_type'),
                'role': role
            }), 200
        except Exception as e:
            return jsonify({'error': 'credenciales invalidas o keycloak no disponible', 'detail': str(e)}), 401

    # Mock fallback for development
    # WARNING: esto es solo para desarrollo local
    if username == 'admin' and password == 'admin':
        return jsonify({
            'access_token': 'mock-access-token',
            'refresh_token': 'mock-refresh-token',
            'expires_in': 3600,
            'token_type': 'bearer',
            'role': 'administrador'
        }), 200

    # simple dev rule: any username with password 'devpass' is allowed
    if password == 'devpass':
        # asignar rol por convención de nombre
        role = 'estudiante'
        if 'admin' in username.lower() or username.lower() == 'admin':
            role = 'administrador'
        elif 'teach' in username.lower() or 'doc' in username.lower():
            role = 'docente'
        return jsonify({
            'access_token': f'mock-token-for-{username}',
            'refresh_token': 'mock-refresh-token',
            'expires_in': 3600,
            'token_type': 'bearer',
            'role': role
        }), 200

    return jsonify({'error': 'credenciales invalidas'}), 401


if __name__ == '__main__':
    # puerto 5000 según solicitud
    app.run(host='0.0.0.0', port=5000, debug=True)
