import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

interface Tarea {
  id: number;
  materia: string;
  titulo: string;
  descripcion: string;
  fechaEntrega: string;
  estado: 'pendiente' | 'entregada' | 'calificada';
  calificacion?: number;
  // Agregar propiedades faltantes
  asignatura: string;
  entrega: string;
  progreso: number;
}

@Component({
  selector: 'app-tareas',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './tareas.html',
  styleUrls: ['./tareas.css']
})
export default class Tareas {
  tareas: Tarea[] = [
    {
      id: 1,
      materia: 'Matemáticas',
      asignatura: 'Matemáticas',
      titulo: 'Ejercicios de Álgebra',
      descripcion: 'Resolver los ejercicios del 1 al 20 de la página 45',
      fechaEntrega: '2024-11-25',
      entrega: '2024-11-25',
      estado: 'pendiente',
      progreso: 0
    },
    {
      id: 2,
      materia: 'Español',
      asignatura: 'Español',
      titulo: 'Ensayo sobre literatura',
      descripcion: 'Escribir un ensayo de 500 palabras sobre "Cien años de soledad"',
      fechaEntrega: '2024-11-22',
      entrega: '2024-11-22',
      estado: 'entregada',
      progreso: 100
    },
    {
      id: 3,
      materia: 'Ciencias',
      asignatura: 'Ciencias',
      titulo: 'Proyecto de laboratorio',
      descripcion: 'Realizar experimento sobre el ciclo del agua',
      fechaEntrega: '2024-11-28',
      entrega: '2024-11-28',
      estado: 'calificada',
      calificacion: 4.5,
      progreso: 100
    }
  ];

  descargar(tarea: Tarea) {
    console.log('Descargando material de tarea:', tarea.titulo);
    alert(`Descargando material de: ${tarea.titulo}\n\nEsta funcionalidad se conectará al backend para descargar archivos adjuntos.`);
  }

  entregar(tarea: Tarea) {
    console.log('Entregando tarea:', tarea.titulo);
    alert(`Subir archivo para: ${tarea.titulo}\n\nNOTA: La funcionalidad de carga de archivos fue eliminada según tu solicitud.\nEn su lugar, se puede marcar como "Entregada" sin archivo.`);
    
    // Marcar como entregada
    tarea.estado = 'entregada';
    tarea.progreso = 100;
  }
}