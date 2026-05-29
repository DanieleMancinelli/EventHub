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

  // Funzione per creare gli header con il Token JWT
  private getHeaders() {
    return new HttpHeaders({
      'Authorization': `Bearer ${this.auth.getToken()}`
    });
  }

  // --- EVENTI ---
  getEventi(filtri: any = {}): Observable<any> {
    // Trasformiamo l'oggetto filtri in parametri URL (es: ?citta=Roma)
    return this.http.get(`${this.apiUrl}/eventi`, { params: filtri });
  }

  getDettaglioEvento(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/eventi/${id}`);
  }

  // --- ORGANIZZATORE (Richiede Token) ---
  creaEvento(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/organizzatore/eventi`, formData, {
      headers: this.getHeaders()
    });
  }

  // --- UTENTE (Richiede Token) ---
  iscriviti(eventoId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/eventi/${eventoId}/iscrizione`, {}, {
      headers: this.getHeaders()
    });
  }

  getMieiBiglietti(): Observable<any> {
    return this.http.get(`${this.apiUrl}/utente/biglietti`, {
      headers: this.getHeaders()
    });
  }
}
