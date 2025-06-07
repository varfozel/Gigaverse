import subprocess
import json
import os

def get_signature_from_node(private_key):
    result = subprocess.run(
        ["node", "signer.js"],
        capture_output=True,
        text=True,
        env={**os.environ, "PRIVATE_KEY": private_key}
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise RuntimeError(result.stderr)

def main(private_key):
    sig_data = get_signature_from_node(private_key)
    return sig_data['signature'], sig_data['address'], sig_data['timestamp']
