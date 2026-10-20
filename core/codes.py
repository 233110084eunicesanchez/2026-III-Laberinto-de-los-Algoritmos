import secrets

def invitation_code():
    return secrets.token_hex(6).upper()
