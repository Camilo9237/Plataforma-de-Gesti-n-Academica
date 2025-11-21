#!/bin/bash

echo "🚀 Iniciando todos los servicios backend..."

# Activar entorno virtual
source backend/.env/bin/activate

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para iniciar un servicio
start_service() {
    local service_name=$1
    local port=$2
    local path="backend/${service_name}"
    
    echo -e "${BLUE}Iniciando ${service_name} en puerto ${port}...${NC}"
    
    cd "$path" || exit
    python app.py &
    echo $! > "/tmp/zappa_${service_name}.pid"
    cd - > /dev/null || exit
    
    echo -e "${GREEN}✓ ${service_name} iniciado (PID: $(cat /tmp/zappa_${service_name}.pid))${NC}"
}

# Iniciar todos los servicios
start_service "login_service" 5000
start_service "students_service" 5001
start_service "teachers_service" 5002
start_service "administrator_service" 5003
start_service "groups_service" 5004
start_service "grades_service" 5005

echo ""
echo -e "${GREEN}✅ Todos los servicios están corriendo!${NC}"
echo ""
echo "📋 Servicios activos:"
echo "   • Login Service:         http://localhost:5000"
echo "   • Students Service:      http://localhost:5001"
echo "   • Teachers Service:      http://localhost:5002"
echo "   • Administrator Service: http://localhost:5003"
echo "   • Groups Service:        http://localhost:5004"
echo "   • Grades Service:        http://localhost:5005"
echo ""
echo "Para detener todos los servicios, ejecuta: ./stop_backend.sh"

# Esperar a que el usuario presione Ctrl+C
wait