import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent implements OnInit {
  auth = inject(AuthService);

  ngOnInit() {
    // Appena l'app parte, controlliamo se l'utente ha permessi speciali o è bannato
    this.auth.syncExtraPerms();
  }
}
