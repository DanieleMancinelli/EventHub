from flask import request, jsonify, g
from functools import wraps
import jwt
import requests
import os
from dotenv import load_dotenv

load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv("REALM")
CLIENT_ID = os.getenv("CLIENT_ID")
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

def get_keycloak_public_key(token: str):
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        response = requests.get(JWKS_URL)
        jwks = response.json()
        for key_data in jwks["keys"]:
            if key_data["kid"] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
    except Exception as e:
        print(f"Errore JWKS: {e}")
    return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token mancante"}), 401
        
        token = auth_header.split(" ")[1]
        try:
            public_key = get_keycloak_public_key(token)
            payload = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False})
            g.user = payload
        except Exception as e:
            print(f"Token non valido: {e}")
            return jsonify({"error": "Sessione scaduta o non valida"}), 401
            
        return f(*args, **kwargs) # Funziona fuori dal try!
    return decorated

def get_roles(payload: dict) -> list:
    return payload.get("realm_access", {}).get("roles", [])

def require_role(role: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if role not in get_roles(g.user):
                return jsonify({"error": "Permesso negato"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
