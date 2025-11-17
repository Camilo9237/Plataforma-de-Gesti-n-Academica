import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login {
  constructor(private router: Router, private api: ApiService) {}

  username: string = '';
  password: string = '';
  loading: boolean = false;
  error: string | null = null;
  success: string | null = null;

  async login(event?: Event) {
    if (event) {
      event.preventDefault();
    }
    this.error = null;
    this.success = null;
    if (!this.username || !this.password) {
      this.error = 'Usuario y contraseña son requeridos';
      return;
    }

    this.loading = true;
    try {
      const data = await this.api.login({ username: this.username, password: this.password }).toPromise();
      if (!data) {
        this.error = 'Error en autenticación';
      } else {
        // almacenar token en localStorage
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
        }
        this.success = 'Autenticación exitosa';
        // Loguear en DevTools que el login fue exitoso
        console.info('Login successful for user:', this.username, 'response:', data);

        // redirigir internamente al dashboard; validar rol permitido antes de navegar
        const role = data.role;
        const allowedRoles = new Set(['administrador', 'docente', 'estudiante']);

        if (!role) {
          // usuario sin rol
          this.error = 'Inicio de sesión correcto pero el usuario no tiene rol asignado.';
          console.error('Login succeeded but no role present in response:', data);
          alert('Acceso denegado: su cuenta no tiene rol asignado. Contacte al administrador.');
          return;
        }

        if (!allowedRoles.has(role)) {
          // rol no permitido
          console.warn('Login with unauthorized role:', role, 'for user:', this.username);
          alert(`Acceso denegado: el rol '${role}' no tiene permisos para acceder a esta aplicación.`);
          return;
        }

        // role válido → navegar al dashboard por rol
        const routeMap: any = { estudiante: '/dashboard/student', docente: '/dashboard/teacher', administrador: '/dashboard/admin' };
        const target = routeMap[role] || '/dashboard';
        this.router.navigate([target]);
      }
    } catch (err: any) {
      this.error = err?.message || 'Error de conexión';
    } finally {
      this.loading = false;
    }
  }
}
