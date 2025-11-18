import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-horario',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './horario.html',
  styleUrls: ['./horario.css']
})
export class Horario {
  // Presentational component for Horario Académico
  downloadPdf() {
    alert('Descargando PDF del horario...');
  }
}
