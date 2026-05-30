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
    if ev[0]['data_evento'] > datetime.now(): return jsonify({"error": "No"}), 400
    db.aggiungi_recensione(id, g.user.get("sub"), g.user.get("preferred_username", "Utente"), request.json['rating'], request.json['commento'])
    return jsonify({"ok": True})

@app.route("/eventi/<int:id>/iscrizione", methods=["POST"])
@require_auth
def isc(id):
    cod = db.iscrivi_utente(id, g.user.get("sub"))
    return jsonify({"codice": cod}) if cod else (jsonify({"error": "No"}), 400)

# NUOVA ROTTA: Cancella un biglietto specifico tramite il suo codice
@app.route("/utente/biglietti/<string:codice>", methods=["DELETE"])
@require_auth
def cancella_biglietto(codice):
    db.disiscrivi_utente(codice, g.user.get("sub"))
    return jsonify({"ok": True})

@app.route("/utente/biglietti", methods=["GET"])
@require_auth
def get_tix(): return jsonify(db.get_biglietti_utente(g.user.get("sub")))

@app.route("/utente/permessi", methods=["GET"])
@require_auth
def get_permessi():
    res = db.fetch_query("SELECT is_banned, is_organizzatore FROM utenti WHERE utente_id = %s", (g.user["sub"],))
    return jsonify(res[0] if res else {"is_banned": 0, "is_organizzatore": 0})

@app.route("/recensioni/<int:id>/segnala", methods=["PUT"])
@require_auth
def seg_rec(id):
    rec = db.fetch_query("SELECT * FROM recensioni WHERE id = %s", (id,))
    if rec and rec[0]['utente_id'] == g.user.get("sub"): return jsonify({"error": "No"}), 400
    db.segnala_recensione(id); return jsonify({"ok": True})

@app.route("/organizzatore/eventi", methods=["GET", "POST"])
@require_auth
@require_role("organizzatore")
def org_ev():
    if request.method == "POST":
        d = request.form; img = request.files.get("immagine")
        db.aggiungi_evento(d['titolo'], d['descrizione'], d['data'], d['luogo'], d['categoria'], d['prezzo'], d['posti'], img.read() if img else None, g.user.get("sub"))
        return jsonify({"ok": True}), 201
    return jsonify(db.get_eventi_per_organizzatore(g.user.get("sub")))

@app.route("/organizzatore/eventi/<int:id>", methods=["DELETE", "PUT"])
@require_auth
@require_role("organizzatore")
def edit_ev(id):
    if request.method == "DELETE": db.elimina_evento(id, g.user.get("sub"))
    else:
        d = request.form; img = request.files.get("immagine")
        db.update_evento(id, d['titolo'], d['descrizione'], d['data'], d['luogo'], d['categoria'], d['prezzo'], d['posti'], img.read() if img else None, g.user.get("sub"))
    return jsonify({"ok": True})

@app.route("/organizzatore/eventi/<int:id>/csv", methods=["GET"])
@require_auth
@require_role("organizzatore")
def get_csv(id):
    iscritti = db.get_iscritti_evento(id); csv_data = "ID_UTENTE,CODE\n"
    for i in iscritti: csv_data += f"{i['utente_id']},{i['codice_biglietto']}\n"
    return Response(csv_data, mimetype="text/csv", headers={"Content-disposition": f"attachment; filename=iscritti_{id}.csv"})

@app.route("/admin/recensioni", methods=["GET"])
@require_auth
@require_role("admin")
def get_segnalate(): return jsonify(db.fetch_query("SELECT r.*, e.titolo FROM recensioni r JOIN eventi e ON r.evento_id = e.id WHERE r.segnalata = 1"))

@app.route("/admin/recensioni/<int:id>", methods=["DELETE"])
@require_auth
@require_role("admin")
def del_rec_admin(id):
    db.execute_query("DELETE FROM recensioni WHERE id = %s", (id,))
    return jsonify({"ok": True})

@app.route("/admin/recensioni/<int:id>/approva", methods=["PUT"])
@require_auth
@require_role("admin")
def app_rec_admin(id):
    db.execute_query("UPDATE recensioni SET segnalata = 0 WHERE id = %s", (id,))
    return jsonify({"ok": True})

@app.route("/admin/utenti", methods=["GET"])
@require_auth
@require_role("admin")
def get_users(): return jsonify(db.get_all_users())

@app.route("/admin/utenti/<string:u_id>/ban", methods=["PUT"])
@require_auth
@require_role("admin")
def ban_user(u_id): db.toggle_ban(u_id); return jsonify({"ok": True})

@app.route("/admin/utenti/<string:u_id>/promuovi", methods=["PUT"])
@require_auth
@require_role("admin")
def promote_user(u_id): db.toggle_organizzatore(u_id); return jsonify({"ok": True})

if __name__ == "__main__": app.run(host='0.0.0.0', port=5000, debug=True)
