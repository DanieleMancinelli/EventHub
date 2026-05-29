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
    return new HttpHeaders({ 'Authorization': `Bearer ${this.auth.getToken()}` });
  }

  getEventi(filtri: any = {}): Observable<any> { return this.http.get(`${this.apiUrl}/eventi`, { params: filtri }); }
  getDettaglioEvento(id: number): Observable<any> { return this.http.get(`${this.apiUrl}/eventi/${id}`); }
  getMieiEventi(): Observable<any> { return this.http.get(`${this.apiUrl}/organizzatore/eventi`, { headers: this.getHeaders() }); }
  creaEvento(formData: FormData): Observable<any> { return this.http.post(`${this.apiUrl}/organizzatore/eventi`, formData, { headers: this.getHeaders() }); }
  esportaIscritti(id: number) { return this.http.get(`${this.apiUrl}/organizzatore/eventi/${id}/csv`, { headers: this.getHeaders(), responseType: 'blob' }); }
  iscriviti(id: number): Observable<any> { return this.http.post(`${this.apiUrl}/eventi/${id}/iscrizione`, {}, { headers: this.getHeaders() }); }
  getMieiBiglietti(): Observable<any> { return this.http.get(`${this.apiUrl}/utente/biglietti`, { headers: this.getHeaders() }); }

  // METODI ADMIN
  getSegnalazioni(): Observable<any> { return this.http.get(`${this.apiUrl}/admin/recensioni`, { headers: this.getHeaders() }); }
  eliminaRecensione(id: number): Observable<any> { return this.http.delete(`${this.apiUrl}/admin/recensioni/${id}`, { headers: this.getHeaders() }); }
  approvaRecensione(id: number): Observable<any> { return this.http.put(`${this.apiUrl}/admin/recensioni/${id}/approva`, {}, { headers: this.getHeaders() }); }
}
