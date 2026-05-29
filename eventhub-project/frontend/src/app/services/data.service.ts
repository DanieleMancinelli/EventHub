import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { AuthService } from '../core/auth.service';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DataService {
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders() {
    return new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    });
  }

  getEventi(filtri: any = {}): Observable<any> {
    return this.http.get(`${this.apiUrl}/eventi`, { params: filtri });
  }

  getDettaglioEvento(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/eventi/${id}`);
  }

  // --- ORGANIZZATORE ---
  getMieiEventi(): Observable<any> {
    return this.http.get(`${this.apiUrl}/organizzatore/eventi`, { headers: this.getHeaders() });
  }

  creaEvento(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/organizzatore/eventi`, formData, { headers: this.getHeaders() });
  }

  esportaIscritti(eventoId: number) {
    // Per scaricare un file servono degli header particolari
    return this.http.get(`${this.apiUrl}/organizzatore/eventi/${eventoId}/csv`, {
      headers: this.getHeaders(),
      responseType: 'blob' // Importante per i file
    });
  }

  // --- UTENTE ---
  iscriviti(eventoId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/eventi/${eventoId}/iscrizione`, {}, { headers: this.getHeaders() });
  }

  getMieiBiglietti(): Observable<any> {
    return this.http.get(`${this.apiUrl}/utente/biglietti`, { headers: this.getHeaders() });
  }
}
