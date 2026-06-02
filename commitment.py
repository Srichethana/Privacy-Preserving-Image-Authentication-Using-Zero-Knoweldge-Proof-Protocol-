import hashlib
import random
def generate_commitment(secret, session_id, nonce):
    r = random.randint(1, 1_000_000)
    data = f"{secret}{r}{session_id}{nonce}"
    commitment = hashlib.sha256(data.encode()).hexdigest()
    return commitment, r