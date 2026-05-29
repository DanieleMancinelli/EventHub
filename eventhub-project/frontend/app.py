from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from db_wrapper import DatabaseWrapper
from auth import require_auth, require_role
from datetime import datetime

app = Flask(__name__)
CORS(app)
db = DatabaseWrapper()

@app.route("/eventi", methods=["GET"])
def lista_eventi(): return jsonify(db.get_eventi_filtrati(request.args.get("categoria"), request.args.get("data"), request.args.get("citta"), request.args.get("prezzo_max")))

@app.route("/eventi/<int:id>", methods=["GET"])
def dettaglio_evento(id):
    ev = db.get_evento_by_id(id)
    if not ev: return jsonify({"error": "No"}), 404
    res = ev[0]; res.pop('immagine_copertina', None); return jsonify(res)

@app.route("/eventi/<int:id>/immagine", methods=["GET"])
def get_img(id):
    ev = db.get_evento_by_id(id)
    if not ev or not ev[0]['immagine_copertina']: return "No", 404
    return Response(ev[0]['immagine_copertina'], mimetype='image/jpeg')

@app.route("/eventi/<int:id>/recensioni", methods=["GET"])
def get_rec(id): return jsonify(db.get_recensioni_evento(id))

@app.route("/eventi/<int:id>/recensione", methods=["POST"])
@require_auth
def post_rec(id):
    ev = db.get_evento_by_id(id)
    if ev[0]['data_evento'] > datetime.now(): return jsonify({"error": "Troppo presto"}), 400
    # Prendiamo preferred_username dal token
    username = g.user.get("preferred_username", "Utente")
    db.aggiungi_recensione(id, g.user.get("sub"), username, request.json['rating'], request.json['commento'])
    return jsonify({"ok": True})

@app.route("/eventi/<int:id>/iscrizione", methods=["POST"])
@require_auth
def isc(id):
    cod = db.iscrivi_utente(id, g.user.get("sub"))
    if not cod: return jsonify({"error": "Posti esauriti o evento passato"}), 400
    return jsonify({"codice": cod}), 201

# ... (Altre rotte rimangono uguali)
@app.route("/organizzatore/eventi", methods=["GET", "POST"])
@require_auth
@require_role("organizzatore")
def org_ev():
    if request.method == "POST":
        d = request.form; img = request.files.get("immagine")
        db.aggiungi_evento(d['titolo'], d['descrizione'], d['data'], d['luogo'], d['categoria'], d['prezzo'], d['posti'], img.read() if img else None, g.user.get("sub"))
        return jsonify({"ok": True}), 201
    return jsonify(db.get_eventi_per_organizzatore(g.user.get("sub")))

@app.route("/utente/biglietti", methods=["GET"])
@require_auth
def get_tix(): return jsonify(db.get_biglietti_utente(g.user.get("sub")))

@app.route("/recensioni/<int:id>/segnala", methods=["PUT"])
@require_auth
def seg_rec(id): db.segnala_recensione(id); return jsonify({"ok": True})

@app.route("/admin/recensioni", methods=["GET"])
@require_auth
@require_role("admin")
def get_segnalate(): return jsonify(db.fetch_query("SELECT r.*, e.titolo FROM recensioni r JOIN eventi e ON r.evento_id = e.id WHERE r.segnalata = TRUE"))

@app.route("/admin/recensioni/<int:id>", methods=["DELETE", "PUT"])
@require_auth
@require_role("admin")
def mod_rec(id):
    if request.method == "DELETE": db.execute_query("DELETE FROM recensioni WHERE id = %s", (id,))
    else: db.execute_query("UPDATE recensioni SET segnalata = FALSE WHERE id = %s", (id,))
    return jsonify({"ok": True})

if __name__ == "__main__": app.run(host='0.0.0.0', port=5000, debug=True)
