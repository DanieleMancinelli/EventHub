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
  
  nuovoEvento = {
    titolo: '',
    descrizione: '',
    data: '',
    luogo: '',
    categoria: 'concerto',
    prezzo: 0,
    posti: 100
  };

  ngOnInit() {
    this.carica();
  }

  carica() {
    this.dataService.getMieiEventi().subscribe({
      next: (res) => this.mieiEventi.set(res),
      error: (err) => console.error("Errore nel caricamento dei tuoi eventi:", err)
    });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  salva() {
    const fd = new FormData();
    fd.append('titolo', this.nuovoEvento.titolo);
    fd.append('descrizione', this.nuovoEvento.descrizione);
    fd.append('data', this.nuovoEvento.data);
    fd.append('luogo', this.nuovoEvento.luogo);
    fd.append('categoria', this.nuovoEvento.categoria);
    fd.append('prezzo', this.nuovoEvento.prezzo.toString());
    fd.append('posti', this.nuovoEvento.posti.toString());
    
    if (this.selectedFile) {
      fd.append('immagine', this.selectedFile);
    }

    this.dataService.creaEvento(fd).subscribe(() => {
      alert("Evento creato con successo!");
      this.carica();
    });
  }

  scaricaCSV(id: number) {
    this.dataService.esportaIscritti(id).subscribe(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `iscritti_evento_${id}.csv`;
      a.click();
    });
  }
}
