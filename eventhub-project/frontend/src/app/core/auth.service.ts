import { Injectable, inject, signal } from '@angular/core';
import Keycloak from 'keycloak-js';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private keycloak = inject(Keycloak);
  private http = inject(HttpClient);
  
  // Segnale per sapere se l'utente è promosso nel DB
  isPromoted = signal(false);

  login() { this.keycloak.login({ redirectUri: window.location.origin }); }
  logout() { this.keycloak.logout({ redirectUri: window.location.origin }); }
  register() { this.keycloak.register({ redirectUri: window.location.origin }); }
  manageAccount() { this.keycloak.accountManagement(); }

  isLoggedIn(): boolean { return !!this.keycloak.authenticated; }
  getUsername(): string { return this.keycloak.tokenParsed?.['preferred_username'] || ''; }
  getUserId(): string { return this.keycloak.tokenParsed?.['sub'] || ''; }
  getToken(): string | undefined { return this.keycloak.token; }
  
  // Carica i permessi extra dal nostro DB Flask
  syncExtraPerms() {
    if (this.isLoggedIn()) {
      this.http.get<any>(`${environment.apiUrl}/utente/permessi`, {
        headers: { 'Authorization': `Bearer ${this.getToken()}` }
      }).subscribe({
        next: (res) => {
          if (res.is_banned) {
            alert("IL TUO ACCOUNT È STATO BANNATO.");
            this.logout();
          }
          this.isPromoted.set(res.is_organizzatore === 1);
        },
        error: (err) => {
          if (err.status === 403) {
            alert("ACCESSO NEGATO: SEI STATO BANNATO.");
            this.logout();
          }
        }
      });
    }
  }

  hasRole(role: string): boolean {
    const roles = this.keycloak.tokenParsed?.['realm_access']?.['roles'] || [];
    // Se cerchiamo 'organizzatore', controlliamo sia Keycloak che il nostro segnale isPromoted
    if (role === 'organizzatore') {
      return roles.includes(role) || this.isPromoted();
    }
    return roles.includes(role);
  }
}
