import os

APP_NAME = "apivouch"
APP_VERSION = "1.1.0"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./apivouch.db")
ALLOW_PRIVATE_NETWORK = os.getenv("ALLOW_PRIVATE_NETWORK", "false").lower() == "true"
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "1"))
MAX_RESPONSE_BYTES = int(os.getenv("MAX_RESPONSE_BYTES", "1048576"))
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "524288"))
MAX_ENDPOINTS = int(os.getenv("MAX_ENDPOINTS", "200"))
MAX_PROJECTS = int(os.getenv("MAX_PROJECTS", "250"))
MAX_REDIRECTS = int(os.getenv("MAX_REDIRECTS", "3"))
MAX_PROOF_PAGES = int(os.getenv("MAX_PROOF_PAGES", "20"))
MAX_PROOF_RECORDS = int(os.getenv("MAX_PROOF_RECORDS", "5000"))
GIT_COMMIT = os.getenv("GIT_COMMIT") or os.getenv("RENDER_GIT_COMMIT") or "dev-local"
PROJECT_SLUG = os.getenv("PROJECT_SLUG", "apivouch")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
CORS_ORIGINS = [v.strip() for v in os.getenv("CORS_ORIGINS", "").split(",") if v.strip()]
