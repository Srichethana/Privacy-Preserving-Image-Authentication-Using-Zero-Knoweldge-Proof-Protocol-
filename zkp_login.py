import time
from image_preprocessing import preprocess_image, generate_image_hash
from commitment import generate_commitment
from authentication_server import generate_challenge, verify_proof, analytics
from session_manager import create_session, validate_session, close_session, generate_nonce
used_images = set()
def zkp_login(username: str, image_path: str, rounds: int = 5):
    try:
        processed_image = preprocess_image(image_path)
        secret = generate_image_hash(processed_image)
    except Exception as e:
        return False, f"Error processing image: {e}", None, None, None
    if secret in used_images:
        analytics.log_failure(username, "Replay attack detected (same image reused)")
        return False, "Authentication Failed - Replay Attack Detected (Image already used)", None, None, None
    session_id, _ = create_session(username)
    start_time = time.time()
    authentication_failed = False
    round_details = []
    round_times = []
    for i in range(rounds):
        round_start = time.time()
        round_info = f"Round {i+1}: "
        if not validate_session(session_id):
            round_info += "Session expired"
            authentication_failed = True
            break
        nonce = generate_nonce(session_id)
        commitment, r = generate_commitment(secret, session_id, nonce)
        challenge = generate_challenge()
        round_info += f"Challenge = {challenge} -> "
        response = r if challenge == 0 else (secret, r)
        result = verify_proof(username, commitment, challenge, response, session_id, nonce)
        if not result:
            round_info += "Verification failed"
            authentication_failed = True
            break
        else:
            round_info += "Passed"
        round_time = round(time.time() - round_start, 4)
        round_times.append(round_time)
        round_details.append(round_info)
    close_session(session_id)
    total_time = round(time.time() - start_time, 4)
    if not authentication_failed:
        used_images.add(secret)          
        analytics.log_success(username)
        return True, "Authentication Successful", total_time, round_details, round_times
    else:
        return False, "Authentication Failed", total_time, round_details, round_times