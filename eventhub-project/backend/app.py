from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from db_wrapper import DatabaseWrapper
from auth import require_auth, require_role
from datetime import datetime

app = Flask(__name__)
CORS(app)
db = DatabaseWrapper()

# --- 1. ROTTE PUBBLICHE (Accessibili a tutti) ---

@app.route("/eventi", methods=["GET"])
def lista_eventi():
    return jsonify(db.get_eventi_filtrati(
        request.args.get("categoria"), 
        request.args.get("data"), 
        request.args.get("citta"), 
        request.args.get("prezzo_max")
    ))

# QUESTA E' LA ROTTA CHE MANCAVA!
@app.route("/eventi/<int:id>", methods=["GET"])
def dettaglio_evento(id):
    evento = db.get_evento_by_id(id)
    if not evento:
        return jsonify({"error": "Evento non trovato"}), 404
    
    res = evento[0]
    # Rimuoviamo il blob dell'immagine dal JSON (lo carichiamo con la rotta sotto)
    res.pop('immagine_copertina', None) 
    return jsonify(res)

@app.route("/eventi/<int:id>/immagine", methods=["GET"])
def get_immagine_evento(id):
    evento = db.get_evento_by_id(id)
    if not evento or not evento[0]['immagine_copertina']:
        return "Immagine non trovata", 404
    return Response(evento[0]['immagine_copertina'], mimetype='image/jpeg')


# --- 2. ROTTE ORGANIZZATORE (Richiedono ruolo 'organizzatore') ---

@app.route("/organizzatore/eventi", methods=["GET"])
@require_auth
@require_role("organizzatore")
def miei_eventi():
    eventi = db.get_eventi_per_organizzatore(g.user.get("sub"))
    for e in eventi: e.pop('immagine_copertina', None)
    return jsonify(eventi)

@app.route("/organizzatore/eventi", methods=["POST"])
@require_auth
@require_role("organizzatore")
def crea_evento():
    d = request.form
    img = request.files.get("immagine")
    img_data = img.read() if img else None
    db.aggiungi_evento(d['titolo'], d['descrizione'], d['data'], d['luogo'], d['categoria'], d['prezzo'], d['posti'], img_data, g.user.get("sub"))
    return jsonify({"status": "ok"}), 201

@app.route("/organizzatore/eventi/<int:id>/csv", methods=["GET"])
@require_auth
@require_role("organizzatore")
def esporta_iscritti(id):
    iscritti = db.get_iscritti_evento(id)
    csv_data = "ID_UTENTE,CODICE_BIGLIETTO\n"
    for i in iscritti: csv_data += f"{i['utente_id']},{i['codice_biglietto']}\n"
    return Response(csv_data, mimetype="text/csv", headers={"Content-disposition": f"attachment; filename=iscritti_{id}.csv"})


# --- 3. ROTTE UTENTE AUTENTICATO (Richiedono solo login) ---

@app.route("/eventi/<int:id>/iscrizione", methods=["POST"])
@require_auth
def iscriviti(id):
    codice = db.iscrivi_utente(id, g.user.get("sub"))
    if codice:
        return jsonify({"codice": codice}), 201
    return jsonify({"error": "Posti esauriti o errore iscrizione"}), 400

@app.route("/utente/biglietti", methods=["GET"])
@require_auth
def miei_biglietti():
    return jsonify(db.get_biglietti_utente(g.user.get("sub")))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
