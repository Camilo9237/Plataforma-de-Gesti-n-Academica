import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-observations',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './observations.html',
  styleUrls: ['./observations.css']
})
export default class ObservationsComponent {
  resumen = { total: 6, positivas: 3, negativas: 2, neutrales: 1 };

  filtros = { texto: '', tipo: 'Todas', grupo: 'Todos los Grupos' };

  observaciones = [
    { id: 1, fecha: '2024-11-18', estudiante: 'Ana María García', grupo: "10ºA", tipo: 'Positiva', descripcion: 'Excelente participación en clase y entrega puntual', seguimiento: 'Felicitación enviada a padres', docente: 'Prof. García' },
    { id: 2, fecha: '2024-11-17', estudiante: 'Carlos Rodríguez', grupo: "10ºA", tipo: 'Negativa', descripcion: 'Comportamiento inadecuado durante la clase', seguimiento: 'Citación a padres programada', docente: 'Prof. García' },
    { id: 3, fecha: '2024-11-16', estudiante: 'María Elena López', grupo: "11ºB", tipo: 'Positiva', descripcion: 'Colaboró con compañeros que presentaban dificultad', seguimiento: 'Reconocimiento público', docente: 'Prof. López' }
  ];

  nuevaObservacion() {
    alert('Abrir formulario para nueva observación (simulado)');
  }

  editar(obs: any) {
    alert(`Editar observación id=${obs.id} (simulado)`);
  }

  eliminar(obs: any) {
    if (confirm('¿Eliminar observación?')) {
      this.observaciones = this.observaciones.filter(o => o.id !== obs.id);
    }
  }
}
