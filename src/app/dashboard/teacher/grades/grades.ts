import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-grades',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './grades.html',
  styleUrls: ['./grades.css']
})
export default class GradesComponent {
  grupos = [
    { id: 'g1', name: "10ºA - Matemáticas" },
    { id: 'g2', name: "11ºB - Física" }
  ];

  periodos = [ 'Periodo 1', 'Periodo 2', 'Periodo 3' ];

  grupoSeleccionado: any = null;
  periodoSeleccionado: any = null;

  estudiantes = [
    { codigo: '2024001', nombre: 'Ana María García', nota1: 4.2, nota2: 3.8, nota3: 4.5, promedio: 4.17, observaciones: 'Excelente participación en clase' },
    { codigo: '2024002', nombre: 'Carlos Rodríguez', nota1: 3.5, nota2: 4.0, nota3: 3.8, promedio: 3.77, observaciones: 'Observaciones...' },
    { codigo: '2024003', nombre: 'María Elena López', nota1: 4.8, nota2: 4.5, nota3: 4.9, promedio: 4.73, observaciones: 'Estudiante destacada' },
    { codigo: '2024004', nombre: 'José Antonio Méndez', nota1: 3.2, nota2: 3.0, nota3: 3.5, promedio: 3.23, observaciones: 'Necesita refuerzo en álgebra' },
    { codigo: '2024005', nombre: 'Laura Sofía Hernández', nota1: 4.0, nota2: 4.2, nota3: 4.1, promedio: 4.10, observaciones: 'Observaciones...' }
  ];

  calcularPromediosAuto() {
    this.estudiantes.forEach(s => {
      const sum = (Number(s.nota1) || 0) + (Number(s.nota2) || 0) + (Number(s.nota3) || 0);
      s.promedio = Math.round((sum / 3) * 100) / 100;
    });
    alert('Promedios calculados automáticamente');
  }

  guardarCalificaciones() {
    alert('Calificaciones guardadas (simulado)');
  }
}
