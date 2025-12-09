import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private lastLoginTime: number = 0;
  private readonly LOGIN_GRACE_PERIOD = 5000; // 5 seconds grace period after login

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    // Track login time
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.lastLoginTime = Date.now();
      }
    });
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    
    // Don't add token to login requests
    const isLoginRequest = req.url.includes('/api/login');
    const isHealthCheck = req.url.includes('/api/health');
    
    let cloned = req;
    if (token && !isLoginRequest && !isHealthCheck) {
      cloned = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      console.log(`Adding token to request: ${req.method} ${req.url}`);
    } else if (!token && !isLoginRequest && !isHealthCheck) {
      console.warn(`No token available for request: ${req.method} ${req.url}`);
    }
    
    return next.handle(cloned).pipe(
      catchError((error: HttpErrorResponse) => {
        // Only handle auth errors for authenticated endpoints (not login or health)
        if (!isLoginRequest && !isHealthCheck && (error.status === 401 || error.status === 422)) {
          const timeSinceLogin = Date.now() - this.lastLoginTime;
          const isRecentLogin = timeSinceLogin < this.LOGIN_GRACE_PERIOD;
          
          console.error('Authentication error on protected endpoint:', {
            url: req.url,
            status: error.status,
            error: error.error,
            hasToken: !!token,
            timeSinceLogin: timeSinceLogin,
            isRecentLogin: isRecentLogin
          });
          
          // Don't logout if we just logged in (grace period)
          // This prevents immediate logout due to token validation delays
          if (isRecentLogin) {
            console.warn('Auth error occurred shortly after login - not logging out (grace period)');
            return throwError(() => error);
          }
          
          // Only logout if we have a token (meaning we thought we were authenticated)
          if (token) {
            console.log('Token exists but request failed - logging out');
            // Small delay before logout to allow error to be displayed
            setTimeout(() => {
              this.authService.logout();
            }, 100);
          }
        }
        return throwError(() => error);
      })
    );
  }
}


