import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-boletines',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './boletines.html',
  styleUrls: ['./boletines.css']
})
export class Boletines {
  // Presentational component for 'Consulta de Boletines'.
  // Data should be provided by parent or API; this component focuses on layout.
  downloadPdf() {
    // placeholder for download action (UI-only)
    alert('Generando PDF...');
  }
}
