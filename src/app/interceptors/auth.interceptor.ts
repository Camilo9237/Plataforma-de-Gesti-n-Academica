import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService, private router: Router) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.auth.getToken();
    let authReq = req;
    if (token) {
      authReq = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
    }
    return next.handle(authReq).pipe(
      catchError(err => {
        if (err.status === 401) {
          alert('Sesión expirada. Inicia sesión nuevamente.');
          this.auth.clear();
          this.router.navigate(['/login']);
        } else if (err.status === 403) {
          alert('No tienes permisos para esta acción.');
        }
        return throwError(() => err);
      })
    );
  }
}
