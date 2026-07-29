"""
Autenticação OAuth 2.0 com cache de token local.
Na primeira execução abre o browser para autorizar; nas seguintes usa o token salvo.
"""

import os
import json
import pickle
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

TOKEN_CACHE = Path(__file__).parent.parent / "cache" / "token.pickle"


def get_credentials(client_secret_path: str):
    """
    Retorna credenciais OAuth2 válidas.
    - Se existir token em cache e ainda válido, usa o cache.
    - Se expirado, tenta renovar automaticamente.
    - Se não existir, abre o browser para autorização (apenas 1x).
    """
    creds = None

    if TOKEN_CACHE.exists():
        try:
            with open(TOKEN_CACHE, "rb") as f:
                creds = pickle.load(f)
        except Exception as e:
            print(f"[Auth] Aviso: não foi possível carregar token em cache ({e}). Um novo token será solicitado.")
            try:
                TOKEN_CACHE.unlink()
            except Exception:
                pass
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[Auth] Renovando token de acesso...")
            creds.refresh(Request())
        else:
            print("[Auth] Abrindo browser para autorização (apenas nesta 1ª vez)...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_CACHE, "wb") as f:
            pickle.dump(creds, f)
        print("[Auth] Token salvo em cache.")

    return creds
