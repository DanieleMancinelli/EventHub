import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-organizzatore-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './organizzatore-dashboard.html',
  styleUrl: './organizzatore-dashboard.css'
})
export class OrganizzatoreDashboardComponent implements OnInit {
  private dataService = inject(DataService);
  mieiEventi = signal<any[]>([]);
  selectedFile: File | null = null;
  editingId: number | null = null;
  nuovoEvento = { titolo: '', descrizione: '', data: '', luogo: '', categoria: 'concerto', prezzo: 0, posti: 100 };

  ngOnInit() { this.carica(); }
  carica() { this.dataService.getMieiEventi().subscribe(res => this.mieiEventi.set(res)); }
  onFileSelected(event: any) { this.selectedFile = event.target.files[0]; }
  
  salva() {
    const fd = new FormData();
    Object.entries(this.nuovoEvento).forEach(([k, v]) => fd.append(k, v.toString()));
    if (this.selectedFile) fd.append('immagine', this.selectedFile);

    if (this.editingId) {
      this.dataService.aggiornaEvento(this.editingId, fd).subscribe(() => { alert("Aggiornato!"); this.reset(); });
    } else {
      this.dataService.creaEvento(fd).subscribe(() => { alert("Creato!"); this.reset(); });
    }
  }

  modifica(e: any) {
    this.editingId = e.id;
    this.nuovoEvento = { 
      titolo: e.titolo, descrizione: e.descrizione, 
      data: e.data_evento.slice(0, 16), // Formato per datetime-local
      luogo: e.luogo, categoria: e.categoria || 'concerto', 
      prezzo: e.prezzo, posti: e.posti_totali 
    };
  }

  reset() { this.editingId = null; this.nuovoEvento = { titolo: '', descrizione: '', data: '', luogo: '', categoria: 'concerto', prezzo: 0, posti: 100 }; this.carica(); }
  elimina(id: number) { if (confirm("Eliminare?")) this.dataService.eliminaEvento(id).subscribe(() => this.carica()); }
  scaricaCSV(id: number) { this.dataService.esportaIscritti(id).subscribe(blob => {
    const a = document.createElement('a'); a.href = window.URL.createObjectURL(blob); a.download = `iscritti_${id}.csv`; a.click();
  }); }
}
