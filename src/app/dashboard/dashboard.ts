import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
<div class="dashboard">
  <div *ngIf="loading">Cargando dashboard...</div>

  <div *ngIf="!loading && error" class="error">
    <h3>Error</h3>
    <p>{{ error }}</p>
    <details *ngIf="details">
      <summary>Detalles</summary>
      <pre>{{ details | json }}</pre>
    </details>
  </div>

  <div *ngIf="!loading && !error" class="welcome">
    <h2>{{ message || ('Bienvenido' + (role ? (' ' + role) : '')) }}</h2>
    <p><strong>Rol:</strong> {{ role || 'desconocido' }}</p>
    <p><strong>Usuario:</strong> {{ user || 'desconocido' }}</p>
    <p><strong>Hora:</strong> {{ time || '' }}</p>
  </div>

</div>
  `,
  styles: [
    ".dashboard { padding: 16px; }",
    ".error { color: #b00020; background:#fff0f0; padding:12px; border-radius:6px }",
    ".welcome { background:#f6ffed; padding:12px; border-radius:6px }",
    "pre { background:#f4f4f4; padding:8px; border-radius:4px }"
  ]
})
export class Dashboard implements OnInit {
  loading: boolean = true;
  message: string | null = null;
  role: string | null = null;
  user: string | null = null;
  time: string | null = null;
  error: string | null = null;
  details: any = null;

  // endpoint del backend que devuelve saludo y rol
  private BACKEND_DASHBOARD_URL = 'http://localhost:5003/dashboard-general';

  ngOnInit(): void {
    this.fetchDashboard();
  }

  async fetchDashboard() {
    this.loading = true;
    this.error = null;
    this.details = null;

    const token = localStorage.getItem('access_token');
    if (!token) {
      this.error = 'No se encontró token de autenticación. Por favor inicia sesión.';
      this.loading = false;
      console.error('No access_token in localStorage');
      return;
    }

    try {
      const resp = await fetch(this.BACKEND_DASHBOARD_URL, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });

      let body: any = null;
      try {
        body = await resp.json();
      } catch (e) {
        body = await resp.text();
      }

      if (!resp.ok) {
        this.error = body?.error || body?.message || `Error del servidor (status ${resp.status})`;
        this.details = { status: resp.status, body };
        console.error('Dashboard request failed', this.details);
      } else {
        this.message = body?.message || null;
        this.role = body?.role || null;
        this.user = body?.user || null;
        this.time = body?.time || null;
      }

    } catch (err: any) {
      this.error = err?.message || 'Error de conexión al backend';
      console.error('Network or fetch error while calling dashboard:', err);
    } finally {
      this.loading = false;
    }
  }

}
