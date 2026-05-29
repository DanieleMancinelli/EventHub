import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  authService.login();
  return false;
};

export const roleGuard = (role: string): CanActivateFn => {
  return () => {
    const authService = inject(AuthService);
    if (authService.hasRole(role)) {
      return true;
    }
    alert('Accesso negato: Permessi insufficienti');
    return false;
  };
};
