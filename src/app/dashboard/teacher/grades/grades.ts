import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../../services/api.service';

interface Estudiante {
  id: number;
  nombre: string;
  codigo: string;
  nota1: number;
  nota2: number;
  nota3: number;
  promedio: number;
  observaciones?: string;
}

@Component({
  selector: 'app-grades',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './grades.html',
  styleUrls: ['./grades.css']
})
export default class GradesComponent {
  asignatura = 'Matemáticas';
  grado = '10° A';
  periodo = 'Periodo 1';
  
  // Propiedades faltantes
  grupos = [
    { id: 'g1', name: '10° A - Matemáticas' },
    { id: 'g2', name: '11° B - Física' }
  ];
  
  periodos = ['Periodo 1', 'Periodo 2', 'Periodo 3', 'Periodo 4'];
  
  grupoSeleccionado: any = null;
  periodoSeleccionado: string = 'Periodo 1';
  
  estudiantes: Estudiante[] = [
    { id: 1, nombre: 'Juan Pérez', codigo: 'EST001', nota1: 4.2, nota2: 3.8, nota3: 4.5, promedio: 4.17, observaciones: '' },
    { id: 2, nombre: 'María García', codigo: 'EST002', nota1: 4.5, nota2: 4.2, nota3: 4.8, promedio: 4.5, observaciones: '' },
    { id: 3, nombre: 'Carlos López', codigo: 'EST003', nota1: 3.5, nota2: 4.0, nota3: 3.8, promedio: 3.77, observaciones: '' }
  ];

  loading = false;
  guardando = false;

  constructor(
    private router: Router,
    private api: ApiService
  ) {}

  calcularPromediosAuto() {
    this.estudiantes = this.estudiantes.map(est => ({
      ...est,
      promedio: Number(((est.nota1 + est.nota2 + est.nota3) / 3).toFixed(2))
    }));
  }

  guardarCalificaciones() {
    const notasInvalidas = this.estudiantes.some(est => 
      est.nota1 < 0 || est.nota1 > 5 ||
      est.nota2 < 0 || est.nota2 > 5 ||
      est.nota3 < 0 || est.nota3 > 5
    );

    if (notasInvalidas) {
      alert('Error: Las notas deben estar entre 0.0 y 5.0');
      return;
    }

    this.guardando = true;
    this.calcularPromediosAuto();
    
    console.log('Guardando calificaciones:', {
      asignatura: this.asignatura,
      grado: this.grado,
      periodo: this.periodo,
      estudiantes: this.estudiantes
    });

    setTimeout(() => {
      this.guardando = false;
      alert('Calificaciones guardadas exitosamente.\n\nNOTA: En producción, el backend debe recalcular los promedios para evitar manipulación.');
    }, 1000);
  }

  exportarPDF() {
    alert('Funcionalidad de exportación a PDF en desarrollo.\n\nSe implementará similar a los boletines de estudiantes.');
  }

  goBack() {
    this.router.navigate(['/dashboard/teacher']);
  }
}