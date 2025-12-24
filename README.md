## Setup
1. Copy `.env.example` to `.env`
2. Generate keys:
```bash
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   python3 -c "import secrets; print(secrets.token_hex(32))"
```
3. Add generated keys to `.env`
4. Run `docker-compose up`