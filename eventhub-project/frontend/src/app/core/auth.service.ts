import { Injectable, inject } from '@angular/core';
import Keycloak from 'keycloak-js';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private keycloak = inject(Keycloak);

  login() { this.keycloak.login({ redirectUri: window.location.origin }); }
  logout() { this.keycloak.logout({ redirectUri: window.location.origin }); }
  register() { this.keycloak.register({ redirectUri: window.location.origin }); }

  isLoggedIn(): boolean { return !!this.keycloak.authenticated; }
  getUsername(): string { return this.keycloak.tokenParsed?.['preferred_username'] || ''; }
  getUserId(): string { return this.keycloak.tokenParsed?.['sub'] || ''; } // NUOVO: Ritorna l'ID univoco (sub)
  getToken(): string | undefined { return this.keycloak.token; }
  
  hasRole(role: string): boolean {
    const roles = this.keycloak.tokenParsed?.['realm_access']?.['roles'] || [];
    return roles.includes(role);
  }
}
