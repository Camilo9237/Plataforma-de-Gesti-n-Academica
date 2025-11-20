import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../../services/api.service';
import { HttpResponse } from '@angular/common/http';

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

  loading = false;

  constructor(private api: ApiService) {}

  solicitar(tipo: any) {
    this.loading = true;
    const studentId = '673df46bfaf2a31cb63b0bbd'; // Mock - obtener del token en producción
    
    this.api.downloadCertificado(studentId, 'estudios').subscribe({
      next: (response: HttpResponse<Blob>) => {
        this.loading = false;
        const blob = response.body;
        if (blob) {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `certificado_${tipo.id}_${new Date().getTime()}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }
      },
      error: (err: any) => {
        this.loading = false;
        console.error('Error al descargar certificado:', err);
        alert('Error al generar el certificado. Intenta nuevamente.');
      }
    });
  }

  descargar(c: any) {
    alert(`Funcionalidad de histórico en desarrollo: ${c.tipo}`);
  }
}