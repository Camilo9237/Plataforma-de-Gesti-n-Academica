import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  private BACKEND_DASHBOARD_URL = 'http://localhost:5003/dashboard-general';

  constructor(private router: Router) {}

  async canActivate(): Promise<boolean | UrlTree> {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.warn('RoleGuard: no access_token');
      alert('No se encontró token de autenticación. Por favor inicia sesión.');
      return this.router.parseUrl('/login');
    }

    try {
      const resp = await fetch(this.BACKEND_DASHBOARD_URL, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/json' }
      });

      if (!resp.ok) {
        let body: any = null;
        try { body = await resp.json(); } catch { body = await resp.text(); }
        console.warn('RoleGuard: dashboard validation failed', { status: resp.status, body });
        if (resp.status === 401) {
          alert('Token inválido o expirado. Por favor inicia sesión de nuevo.');
        } else if (resp.status === 403) {
          const role = body?.role ?? 'desconocido';
          alert(`Acceso denegado: el rol '${role}' no está autorizado.`);
        } else {
          alert('Error al validar permisos. Reintenta más tarde.');
        }
        return this.router.parseUrl('/login');
      }

      // OK -> allow navigation
      console.info('RoleGuard: access granted');
      return true;
    } catch (err: any) {
      console.error('RoleGuard: network error validating role', err);
      alert('Error de conexión al validar permisos. Reintenta más tarde.');
      return this.router.parseUrl('/login');
    }
  }
}
