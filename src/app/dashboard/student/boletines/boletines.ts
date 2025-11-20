import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../../services/api.service';
import { HttpResponse } from '@angular/common/http';

@Component({
  selector: 'app-boletines',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './boletines.html',
  styleUrls: ['./boletines.css']
})
export class Boletines {
  loading = false;

  constructor(private api: ApiService) {}

  downloadPdf() {
    this.loading = true;
    const studentId = '673df46bfaf2a31cb63b0bbd'; // Mock
    const periodo = 'Periodo 1';

    this.api.downloadBoletin(studentId, periodo).subscribe({
      next: (response: HttpResponse<Blob>) => {
        this.loading = false;
        const blob = response.body;
        if (blob) {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `boletin_${periodo}_${new Date().getTime()}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }
      },
      error: (err: any) => {
        this.loading = false;
        console.error('Error al descargar boletín:', err);
        alert('Error al generar el boletín. Intenta nuevamente.');
      }
    });
  }
}