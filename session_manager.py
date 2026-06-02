import time
import uuid
active_sessions = {}
used_nonces = set()
def create_session(username):
    session_id = str(uuid.uuid4())
    timestamp = time.time()
    active_sessions[session_id] = {
        "user": username,
        "time": timestamp,
        "nonce": None
    }
    return session_id, timestamp
def generate_nonce(session_id):
    if session_id not in active_sessions:
        return None
    nonce = str(uuid.uuid4())
    active_sessions[session_id]["nonce"] = nonce
    return nonce
def validate_nonce(session_id, nonce):
    if session_id not in active_sessions:
        return False
    session = active_sessions[session_id]
    if session["nonce"] != nonce or nonce in used_nonces:
        return False
    used_nonces.add(nonce)
    return True
def validate_session(session_id, timeout=120):   
    if session_id not in active_sessions:
        return False
    if time.time() - active_sessions[session_id]["time"] > timeout:
        del active_sessions[session_id]
        return False
    return True
def close_session(session_id):
    active_sessions.pop(session_id, None)