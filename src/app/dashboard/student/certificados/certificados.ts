import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-certificados',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './certificados.html',
  styleUrls: ['./certificados.css'],
})
export default class CertificadosComponent {
  tipos = [
    { id: 'estudio', nombre: 'Certificado de Estudios', descripcion: 'Certifica los estudios cursados' },
    { id: 'calificaciones', nombre: 'Certificado de Calificaciones', descripcion: 'Detalle de calificaciones por periodo' },
    { id: 'comportamiento', nombre: 'Certificado de Conducta', descripcion: 'Registro de conducta y observaciones' },
    { id: 'notas', nombre: 'Certificado de Notas Históricas', descripcion: 'Histórico de notas por asignatura' },
    { id: 'otros', nombre: 'Certificado de Asistencia', descripcion: 'Registro de asistencia por periodo' },
  ];

  misCertificados = [
    { id: 1, tipo: 'Certificado de Estudios', fecha: '2024-11-10', formato: 'PDF', descargable: true },
    { id: 2, tipo: 'Certificado de Calificaciones', fecha: '2024-10-25', formato: 'PDF', descargable: true },
  ];

  solicitar(tipo: any) {
    alert(`Solicitud enviada: ${tipo.nombre}`);
  }

  descargar(c: any) {
    alert(`Descargando: ${c.tipo}`);
  }
}
