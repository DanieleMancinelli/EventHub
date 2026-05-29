from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from db_wrapper import DatabaseWrapper
from auth import require_auth, require_role

app = Flask(__name__)
CORS(app)
db = DatabaseWrapper()

# 1. Lista eventi (Pubblica)
@app.route("/eventi", methods=["GET"])
def lista_eventi():
    cat = request.args.get("categoria")
    data = request.args.get("data")
    luogo = request.args.get("citta")
    prezzo = request.args.get("prezzo_max")
    
    eventi = db.get_eventi_filtrati(cat, data, luogo, prezzo)
    return jsonify(eventi)

# 2. Dettaglio evento (Pubblica)
@app.route("/eventi/<int:id>", methods=["GET"])
def dettaglio_evento(id):
    evento = db.get_evento_by_id(id)
    if not evento:
        return jsonify({"error": "Evento non trovato"}), 404
    
    res = evento[0]
    # Rimuoviamo il campo immagine dal JSON perché non è testo
    # Lo vedremo tramite la rotta dedicata qui sotto
    res.pop('immagine_copertina', None) 
    return jsonify(res)

# 3. Rotta per l'immagine (Pubblica)
# Questa rotta serve a "trasformare" il BLOB del database in un'immagine vera
@app.route("/eventi/<int:id>/immagine", methods=["GET"])
def get_immagine_evento(id):
    evento = db.get_evento_by_id(id)
    if not evento or not evento[0]['immagine_copertina']:
        return "Immagine non trovata", 404
    
    # Restituiamo i dati binari dicendo al browser che è un'immagine JPEG
    return Response(evento[0]['immagine_copertina'], mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
