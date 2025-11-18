import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-informes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './informes.html',
  styleUrls: ['./informes.css']
})
export class Informes {
  constructor(private router: Router) {}

  goBack() {
    this.router.navigate(['/dashboard/admin']);
  }
}
