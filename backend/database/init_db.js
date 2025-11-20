// ==========================================
//   REINICIAR BASE DE DATOS
// ==========================================
use colegio;
db.dropDatabase();

print("✔ Base de datos 'colegio' eliminada");

use colegio;

// ==========================================
//   COLECCIÓN: USUARIOS
// ==========================================
db.createCollection("usuarios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["correo", "rol", "nombres", "apellidos"],
      properties: {
        correo: { bsonType: "string", description: "Correo único del usuario" },
        rol: {
          enum: ["administrador", "docente", "estudiante"],
          description: "Rol del usuario"
        },
        nombres: { bsonType: "string" },
        apellidos: { bsonType: "string" },
        creado_en: { bsonType: "timestamp" },
        activo: { bsonType: "bool" },

        // Datos adicionales por rol
        telefono: { bsonType: "string" },
        documento: { bsonType: "string" }, // 🆕 AGREGADO

        // Docente
        codigo_empleado: { bsonType: "string" },
        especialidad: { bsonType: "string" },
        fecha_ingreso: { bsonType: "date" },

        // Estudiante
        codigo_est: { bsonType: "string" },
        fecha_nacimiento: { bsonType: "date" },
        direccion: { bsonType: "string" },
        nombre_acudiente: { bsonType: "string" },
        telefono_acudiente: { bsonType: "string" }
      }
    }
  }
});

// Índices
db.usuarios.createIndex({ correo: 1 }, { unique: true });
db.usuarios.createIndex({ rol: 1 });
db.usuarios.createIndex({ codigo_empleado: 1 }, { sparse: true });
db.usuarios.createIndex({ codigo_est: 1 }, { sparse: true });
db.usuarios.createIndex({ documento: 1 }, { sparse: true }); // 🆕 AGREGADO

print("✔ Colección 'usuarios' creada con índices");

// ==========================================
//   COLECCIÓN: CURSOS
// ==========================================
db.createCollection("cursos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre_curso", "codigo_curso", "periodo"],
      properties: {
        nombre_curso: { bsonType: "string" },
        codigo_curso: { bsonType: "string" },
        id_docente: { bsonType: "objectId" },
        grado: { bsonType: "string" },
        periodo: {
          enum: ["1", "2", "3", "4"],
          description: "Periodo académico"
        },
        capacidad_max: { bsonType: "int" },
        activo: { bsonType: "bool" },
        docente_info: {
          bsonType: "object",
          properties: {
            nombres: { bsonType: "string" },
            apellidos: { bsonType: "string" },
            especialidad: { bsonType: "string" }
          }
        }
      }
    }
  }
});

db.cursos.createIndex({ codigo_curso: 1 }, { unique: true });
db.cursos.createIndex({ id_docente: 1 });
db.cursos.createIndex({ grado: 1, periodo: 1 });

print("✔ Colección 'cursos' creada con índices");

// ==========================================
//   COLECCIÓN: MATRICULAS
// ==========================================
db.createCollection("matriculas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_estudiante", "id_curso"],
      properties: {
        id_estudiante: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        fecha_matricula: { bsonType: "timestamp" },
        estado: {
          enum: ["activo", "finalizado", "retirado", "pendiente"], // 🆕 Agregado "pendiente"
          description: "Estado de la matrícula"
        },
        calificaciones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              tipo: { bsonType: "string" },
              nota: { bsonType: ["double", "int"] },  // ✅ Acepta ambos tipos
              nota_maxima: { bsonType: ["double", "int"] },  // ✅ Acepta ambos tipos
              peso: { bsonType: ["double", "int"] },  // ✅ Acepta ambos tipos
              fecha_eval: { bsonType: "date" },
              comentarios: { bsonType: "string" }
            }
          }
        },
        estudiante_info: {
          bsonType: "object",
          properties: {
            nombres: { bsonType: "string" },
            apellidos: { bsonType: "string" },
            codigo_est: { bsonType: "string" }
          }
        },
        curso_info: {
          bsonType: "object",
          properties: {
            nombre_curso: { bsonType: "string" },
            codigo_curso: { bsonType: "string" },
            grado: { bsonType: "string" },
            periodo: { bsonType: "string" }
          }
        }
      }
    }
  }
});

db.matriculas.createIndex({ id_estudiante: 1, id_curso: 1 }, { unique: true });
db.matriculas.createIndex({ id_estudiante: 1 });
db.matriculas.createIndex({ id_curso: 1 });
db.matriculas.createIndex({ estado: 1 }); // 🆕 AGREGADO

print("✔ Colección 'matriculas' creada con índices");

// ==========================================
//   COLECCIÓN: REPORTES
// ==========================================
db.createCollection("reportes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tipo_reporte", "generado_por"],
      properties: {
        tipo_reporte: {
          enum: ["boletin", "resumen_curso", "rendimiento_docente", "certificado"]
        },
        generado_por: { bsonType: "objectId" },
        id_estudiante: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        id_docente: { bsonType: "objectId" },
        fecha_generado: { bsonType: "timestamp" },
        datos_reporte: {
          bsonType: "object",
          description: "Datos específicos del reporte"
        }
      }
    }
  }
});

db.reportes.createIndex({ tipo_reporte: 1 });
db.reportes.createIndex({ fecha_generado: 1 });

print("✔ Colección 'reportes' creada con índices");

// ==========================================
//   COLECCIÓN: CERTIFICADOS
// ==========================================
db.createCollection("certificados", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_estudiante", "tipo_certificado", "fecha_emision"], // 🔧 id_curso ya no es obligatorio
      properties: {
        id_estudiante: { bsonType: "objectId" },
        id_curso: { bsonType: "objectId" },
        tipo_certificado: { bsonType: "string" },
        fecha_emision: { bsonType: "date" },
        emitido_por: { bsonType: "objectId" },
        datos_certificado: {
          bsonType: "object"
        }
      }
    }
  }
});

db.certificados.createIndex({ id_estudiante: 1 });
db.certificados.createIndex({ fecha_emision: 1 });

print("✔ Colección 'certificados' creada con índices");

// ==========================================
//   COLECCIÓN: AUDITORÍA
// ==========================================
db.createCollection("auditoria", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["accion"],
      properties: {
        id_usuario: { bsonType: "objectId" },
        accion: { bsonType: "string" },
        id_entidad: { bsonType: "objectId" },
        detalles: { bsonType: ["string", "object"] }, // 🔧 Permitir objeto también
        fecha: { bsonType: "timestamp" },
        entidad_afectada: { bsonType: "string" },
        ip: { bsonType: "string" } // 🆕 AGREGADO
      }
    }
  }
});

db.auditoria.createIndex({ id_usuario: 1 });
db.auditoria.createIndex({ accion: 1 });
db.auditoria.createIndex({ fecha: 1 });

print("✔ Colección 'auditoria' creada con índices");
print("✅ Esquema de base de datos creado exitosamente");