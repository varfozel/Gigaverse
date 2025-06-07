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

if __name__ == "__main__":
    # For testing purposes
    test_key = "0x883efd2c292029f553d86ed1d6950685ab131788dee59ecb293a8305cc80d993"
    signature, address, timestamp = main(test_key)
    print(signature, address, timestamp)