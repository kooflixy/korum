import subprocess
from pathlib import Path

CERTS_DIR = Path(__file__).resolve().parent.parent / "certs"

private_key = CERTS_DIR / "private.pem"
public_key = CERTS_DIR / "public.pem"


def main():
    CERTS_DIR.mkdir(exist_ok=True)

    if private_key.exists() or public_key.exists():
        print("Keys already exist. Skipping generation.")
        return

    subprocess.run(
        ["openssl", "genrsa", "-out", str(private_key), "2048"],
        check=True,
    )

    subprocess.run(
        ["openssl", "rsa", "-in", str(private_key), "-pubout", "-out", str(public_key)],
        check=True,
    )

    print("RSA keys generated successfully.")


if __name__ == "__main__":
    main()
