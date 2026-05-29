from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from db_wrapper import DatabaseWrapper
from auth import require_auth, require_role
from datetime import datetime

app = Flask(__name__)
CORS(app)
db = DatabaseWrapper()

# --- PUBBLICO ---
@app.route("/eventi", methods=["GET"])
def lista_eventi():
    return jsonify(db.get_eventi_filtrati(request.args.get("categoria"), request.args.get("data"), request.args.get("citta"), request.args.get("prezzo_max")))

@app.route("/eventi/<int:id>/immagine", methods=["GET"])
def get_immagine_evento(id):
    evento = db.get_evento_by_id(id)
    if not evento or not evento[0]['immagine_copertina']: return "No image", 404
    return Response(evento[0]['immagine_copertina'], mimetype='image/jpeg')

# --- ORGANIZZATORE ---
@app.route("/organizzatore/eventi", methods=["POST"])
@require_auth
@require_role("organizzatore")
def crea_evento():
    d = request.form
    img = request.files.get("immagine")
    db.aggiungi_evento(d['titolo'], d['descrizione'], d['data'], d['luogo'], d['categoria'], d['prezzo'], d['posti'], img.read() if img else None, g.user.get("sub"))
    return jsonify({"status": "ok"}), 201

@app.route("/organizzatore/eventi/<int:id>/csv", methods=["GET"])
@require_auth
@require_role("organizzatore")
def esporta_iscritti(id):
    iscritti = db.get_iscritti_evento(id)
    # Creiamo il file CSV come una semplice stringa di testo
    csv_data = "ID_UTENTE,CODICE_BIGLIETTO\n"
    for i in iscritti:
        csv_data += f"{i['utente_id']},{i['codice_biglietto']}\n"
    
    return Response(csv_data, mimetype="text/csv", headers={"Content-disposition": f"attachment; filename=iscritti_{id}.csv"})

# --- UTENTE ---
@app.route("/eventi/<int:id>/iscrizione", methods=["POST"])
@require_auth
def iscriviti(id):
    codice = db.iscrivi_utente(id, g.user.get("sub"))
    return jsonify({"codice": codice}) if codice else (jsonify({"error": "No posti"}), 400)

@app.route("/utente/biglietti", methods=["GET"])
@require_auth
def miei_biglietti():
    return jsonify(db.get_biglietti_utente(g.user.get("sub")))

@app.route("/recensioni/<int:id>/segnala", methods=["PUT"])
@require_auth
def segnala(id):
    db.segnala_recensione(id)
    return jsonify({"status": "segnalata"})

# --- ADMIN ---
@app.route("/admin/recensioni", methods=["GET"])
@require_auth
@require_role("admin")
def recensioni_segnalate():
    return jsonify(db.get_recensioni_segnalate())

@app.route("/admin/recensioni/<int:id>", methods=["DELETE"])
@require_auth
@require_role("admin")
def elimina_recensione(id):
    db.elimina_recensione(id)
    return jsonify({"status": "eliminata"})

@app.route("/admin/recensioni/<int:id>/approva", methods=["PUT"])
@require_auth
@require_role("admin")
def approva_recensione(id):
    db.approva_recensione(id)
    return jsonify({"status": "approvata"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
