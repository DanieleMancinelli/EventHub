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
  private getHeaders() { return new HttpHeaders({ 'Authorization': `Bearer ${this.auth.getToken()}` }); }

  getEventi(f: any = {}): Observable<any> { return this.http.get(`${this.apiUrl}/eventi`, { params: f }); }
  getDettaglioEvento(id: number): Observable<any> { return this.http.get(`${this.apiUrl}/eventi/${id}`); }
  getMieiEventi(): Observable<any> { return this.http.get(`${this.apiUrl}/organizzatore/eventi`, { headers: this.getHeaders() }); }
  creaEvento(fd: FormData): Observable<any> { return this.http.post(`${this.apiUrl}/organizzatore/eventi`, fd, { headers: this.getHeaders() }); }
  aggiornaEvento(id: number, fd: FormData): Observable<any> { return this.http.put(`${this.apiUrl}/organizzatore/eventi/${id}`, fd, { headers: this.getHeaders() }); }
  eliminaEvento(id: number): Observable<any> { return this.http.delete(`${this.apiUrl}/organizzatore/eventi/${id}`, { headers: this.getHeaders() }); }
  esportaIscritti(id: number) { return this.http.get(`${this.apiUrl}/organizzatore/eventi/${id}/csv`, { headers: this.getHeaders(), responseType: 'blob' }); }
  iscriviti(id: number): Observable<any> { return this.http.post(`${this.apiUrl}/eventi/${id}/iscrizione`, {}, { headers: this.getHeaders() }); }
  disiscriviti(codice: string): Observable<any> { return this.http.delete(`${this.apiUrl}/utente/biglietti/${codice}`, { headers: this.getHeaders() }); }
  getMieiBiglietti(): Observable<any> { return this.http.get(`${this.apiUrl}/utente/biglietti`, { headers: this.getHeaders() }); }
  getRecensioni(id: number): Observable<any> { return this.http.get(`${this.apiUrl}/eventi/${id}/recensioni`); }
  inviaRecensione(id: number, data: any): Observable<any> { return this.http.post(`${this.apiUrl}/eventi/${id}/recensione`, data, { headers: this.getHeaders() }); }
  segnalaRecensione(id: number): Observable<any> { return this.http.put(`${this.apiUrl}/recensioni/${id}/segnala`, {}, { headers: this.getHeaders() }); }
  getSegnalazioni(): Observable<any> { return this.http.get(`${this.apiUrl}/admin/recensioni`, { headers: this.getHeaders() }); }
  eliminaRecensione(id: number): Observable<any> { return this.http.delete(`${this.apiUrl}/admin/recensioni/${id}`, { headers: this.getHeaders() }); }
  approvaRecensione(id: number): Observable<any> { return this.http.put(`${this.apiUrl}/admin/recensioni/${id}/approva`, {}, { headers: this.getHeaders() }); }
  getUtenti(): Observable<any> { return this.http.get(`${this.apiUrl}/admin/utenti`, { headers: this.getHeaders() }); }
  toggleBan(id: string): Observable<any> { return this.http.put(`${this.apiUrl}/admin/utenti/${id}/ban`, {}, { headers: this.getHeaders() }); }
  togglePromuovi(id: string): Observable<any> { return this.http.put(`${this.apiUrl}/admin/utenti/${id}/promuovi`, {}, { headers: this.getHeaders() }); }
}
