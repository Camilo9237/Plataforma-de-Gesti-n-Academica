import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-attendance',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './attendance.html',
  styleUrls: ['./attendance.css']
})
export default class AttendanceComponent {
  grupos = [ { id: 'g1', name: '10ºA - Matemáticas' }, { id: 'g2', name: '11ºB - Física' } ];
  periodos = ['Periodo 1','Periodo 2','Periodo 3'];
  grupoSeleccionado: any = null;
  periodoSeleccionado: any = null;
  fechaSeleccionada: string = new Date().toISOString().slice(0,10);

  estudiantes = [
    { codigo: '2024001', nombre: 'Ana María García', presente: true },
    { codigo: '2024002', nombre: 'Carlos Rodríguez', presente: true },
    { codigo: '2024003', nombre: 'María Elena López', presente: true },
    { codigo: '2024004', nombre: 'José Antonio Méndez', presente: false },
    { codigo: '2024005', nombre: 'Laura Sofía Hernández', presente: true }
  ];

  marcarTodos(valor: boolean) {
    this.estudiantes.forEach(s => s.presente = valor);
  }

  guardarAsistencia() {
    alert('Asistencia guardada (simulado)');
  }
}
