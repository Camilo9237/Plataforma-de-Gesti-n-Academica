import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-tareas',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './tareas.html',
  styleUrls: ['./tareas.css'],
})
export default class TareasComponent {
  // Datos de ejemplo para presentación
  tareas = [
    {
      id: 1,
      titulo: 'Ejercicios de Cálculo Diferencial',
      asignatura: 'Matemáticas',
      entrega: '2024-11-22',
      progreso: 0,
      estado: 'Pendiente',
    },
    {
      id: 2,
      titulo: 'Ensayo sobre Literatura Colombiana',
      asignatura: 'Español',
      entrega: '2024-11-20',
      progreso: 60,
      estado: 'En Progreso',
    },
    {
      id: 3,
      titulo: 'Laboratorio de Química',
      asignatura: 'Ciencias',
      entrega: '2024-11-19',
      progreso: 20,
      estado: 'Retrasado',
    },
  ];

  descargar(tarea: any) {
    alert(`Descargando tarea: ${tarea.titulo}`);
  }

  entregar(tarea: any) {
    alert(`Entregar tarea: ${tarea.titulo}`);
  }
}
