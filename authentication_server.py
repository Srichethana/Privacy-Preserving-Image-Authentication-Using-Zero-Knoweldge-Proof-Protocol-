import secrets
import hashlib
import json
from session_manager import validate_session, validate_nonce
from auth_failure_analytics import AuthFailureAnalytics
DATABASE = "users.json"
analytics = AuthFailureAnalytics()
def load_users():
    try:
        with open(DATABASE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def generate_challenge():
    return secrets.randbelow(2)
def verify_proof(username, commitment, challenge, response, session_id, nonce):
    if not validate_session(session_id):
        analytics.log_failure(username, "Session expired")
        return False   
    if not validate_nonce(session_id, nonce):
        analytics.log_failure(username, "Replay attack detected (nonce reuse)")
        return False
    users = load_users()
    if username not in users:
        analytics.log_failure(username, "Unknown user")
        return False
    return True