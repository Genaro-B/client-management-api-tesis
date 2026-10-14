"""Mide la latencia de la API real y su estabilidad, con un run reproducible.

Levanta el backend FastAPI contra una base SQLite temporal (se crean datos de
semilla, no se toca `dev.db`), autentica, y ejecuta dos fases:

1. **Latencia** — 30 solicitudes consecutivas por cada uno de los cinco
   endpoints de la Tabla 5, sin calentamiento previo, registrando el tiempo
   total de la petición con `time.perf_counter()`. De esa fase salen la media,
   la mediana, el percentil 95, el mínimo, el máximo, la desviación, el
   intervalo de confianza y el CV.
2. **Estabilidad** — un volumen mayor de solicitudes alternadas entre los
   mismos endpoints, contando los códigos de estado por familia para
   contrastar el umbral de ≥ 1 % de errores 5xx.

Requiere únicamente el entorno virtual del proyecto. No necesita Telegram,
n8n ni red externa: la API corre en 127.0.0.1.

    python tools/medicion-tiempos/medir.py
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

from stats import (
    coeficiente_variacion,
    desviacion,
    intervalo_confianza,
    media,
    mediana,
    percentil,
    resumen_estabilidad,
)

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SALIDA = Path(__file__).resolve().parent / "resultados.json"

N_LATENCIA = 30
N_ESTABILIDAD = 1000
TIEMPO_ARRANQUE_S = 60

# Los cinco endpoints de la Tabla 5, en el orden en que se reportan.
ENDPOINTS = [
    ("GET /clients/{id}", "GET", "/api/v1/clients/{id}", 200, "jwt"),
    ("GET /products/", "GET", "/api/v1/products/", 200, "jwt"),
    ("GET /clients/", "GET", "/api/v1/clients/", 200, "jwt"),
    ("GET /metrics/dashboard", "GET", "/api/v1/metrics/dashboard", 200, "jwt"),
    ("POST /interactions/", "POST", "/api/v1/interactions/", 201, "api-key"),
]

API_KEY = "dev-api-key-123"
ADMIN_EMAIL = "admin@medicion-tesis.com.ar"
ADMIN_PASSWORD = "cambiar123"


def puerto_libre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def preparar_base(ruta_db: Path) -> int:
    """Crea las tablas en una SQLite temporal y siembra datos de medición.

    Devuelve el id de un cliente existente, que es el que usa el endpoint
    `GET /clients/{id}` de la Tabla 5.
    """
    sys.path.insert(0, str(BACKEND))
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from src.core.security import hash_password
    from src.database.base import Base
    from src.models.client import Client
    from src.models.product import Product

    engine = create_engine(f"sqlite:///{ruta_db}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    session.add(
        Client(
            nombre="Admin",
            apellido="Medicion",
            email=ADMIN_EMAIL,
            role="admin",
            password_hash=hash_password(ADMIN_PASSWORD),
            password_change_required=False,
        )
    )
    for i in range(1, 21):
        session.add(
            Client(
                nombre=f"Cliente {i}",
                apellido=f"Apellido {i}",
                email=f"cliente{i}@medicion-tesis.com.ar",
                telefono=f"+5411{1000000 + i}",
            )
        )
    for i in range(1, 11):
        session.add(
            Product(
                nombre=f"Producto {i}",
                descripcion=f"Producto de medición {i}",
                precio=1000.0 + i,
                stock=10,
            )
        )
    session.commit()
    cliente_id = session.query(Client).filter_by(email="cliente1@medicion-tesis.com.ar").first().id
    session.close()
    engine.dispose()
    return cliente_id


def arrancar_api(
    puerto: int, ruta_db: Path, ruta_uploads: Path, log
) -> subprocess.Popen:
    """Arranca uvicorn como subproceso.

    El `stderr` va a un archivo, nunca a PIPE: si el buffer del pipe se llena
    y nadie lo lee, el proceso hijo se bloquea en el `write` y la API deja de
    responder, que es exactamente el síntoma que motivó este cambio.
    """
    entorno = dict(os.environ)
    entorno["DATABASE_URL"] = f"sqlite:///{ruta_db}"
    entorno["UPLOAD_DIR"] = str(ruta_uploads)
    entorno["PYTHONIOENCODING"] = "utf-8"
    return subprocess.Popen(
        [
            str(PYTHON), "-m", "uvicorn", "src.main:app",
            "--host", "127.0.0.1", "--port", str(puerto),
            "--log-level", "warning",
        ],
        cwd=str(BACKEND),
        env=entorno,
        stdout=log,
        stderr=subprocess.STDOUT,
    )


def esperar_listo(
    url_base: str, proceso: subprocess.Popen, ruta_log: Path, tiempo_max: int = TIEMPO_ARRANQUE_S
) -> None:
    limite = time.time() + tiempo_max
    while time.time() < limite:
        if proceso.poll() is not None:
            detalle = ruta_log.read_text(encoding="utf-8", errors="replace")
            raise RuntimeError(f"el backend terminó antes de estar listo:\n{detalle[-2000:]}")
        try:
            if httpx.get(f"{url_base}/openapi.json", timeout=1.0).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"el backend no respondió en {tiempo_max} s")


def obtener_token(url_base: str, http: httpx.Client) -> str:
    respuesta = http.post(
        f"{url_base}/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10.0,
    )
    respuesta.raise_for_status()
    return respuesta.json()["access_token"]


def construir_solicitudes(url_base: str, token: str, cliente_id: int) -> list[dict]:
    """Una definición por endpoint: método, URL, headers y cuerpo."""
    solicitudes = []
    for clave, metodo, ruta, esperado, auth in ENDPOINTS:
        url = url_base + ruta.replace("{id}", str(cliente_id))
        headers = {"X-Api-Key": API_KEY} if auth == "api-key" else {"Authorization": f"Bearer {token}"}
        cuerpo = {"source": "telegram", "payload": "mensaje de medición"} if metodo == "POST" else None
        solicitudes.append(
            {
                "clave": clave,
                "metodo": metodo,
                "url": url,
                "headers": headers,
                "json": cuerpo,
                "esperado": esperado,
            }
        )
    return solicitudes


def disparar(http: httpx.Client, solicitud: dict) -> tuple[int, float]:
    """Dispara una petición y devuelve (código de estado, milisegundos)."""
    inicio = time.perf_counter()
    if solicitud["metodo"] == "POST":
        r = http.post(solicitud["url"], headers=solicitud["headers"], json=solicitud["json"])
    else:
        r = http.get(solicitud["url"], headers=solicitud["headers"])
    duracion_ms = (time.perf_counter() - inicio) * 1000
    return r.status_code, duracion_ms


def medir_latencia(http: httpx.Client, solicitudes: list[dict], n: int) -> dict:
    """n solicitudes consecutivas por endpoint, sin calentamiento."""
    muestras: dict[str, list[float]] = {s["clave"]: [] for s in solicitudes}
    estados: dict[str, int] = {}
    for solicitud in solicitudes:
        for i in range(n):
            codigo, ms = disparar(http, solicitud)
            muestras[solicitud["clave"]].append(ms)
            estados[solicitud["clave"]] = codigo
            if (i + 1) % 10 == 0:
                print(f"      {solicitud['clave']}: {i + 1}/{n}", flush=True)
    resumen = {}
    for clave, valores in muestras.items():
        bajo, alto = intervalo_confianza(valores)
        resumen[clave] = {
            "esperado": estados[clave],
            "n": len(valores),
            "media": media(valores),
            "mediana": mediana(valores),
            "p95": percentil(valores, 95),
            "minimo": min(valores),
            "maximo": max(valores),
            "desviacion": desviacion(valores),
            "ic95": [bajo, alto],
            "cv": coeficiente_variacion(valores),
            "muestras": [round(v, 3) for v in valores],
        }
    return resumen


def medir_estabilidad(http: httpx.Client, solicitudes: list[dict], total: int) -> dict:
    """`total` solicitudes alternadas entre los endpoints; sólo se cuentan estados."""
    codigos = []
    inicio = time.perf_counter()
    for i in range(total):
        solicitud = solicitudes[i % len(solicitudes)]
        codigo, _ = disparar(http, solicitud)
        codigos.append(codigo)
    duracion = time.perf_counter() - inicio
    resumen = resumen_estabilidad(codigos)
    resumen["duracion_s"] = duracion
    resumen["solicitudes_por_segundo"] = total / duracion if duracion else 0.0
    resumen["por_codigo"] = {
        str(c): codigos.count(c) for c in sorted(set(codigos))
    }
    return resumen


def main() -> int:
    with tempfile.TemporaryDirectory(
        prefix="medicion-tiempos-", ignore_cleanup_errors=True
    ) as tmp:
        tmp_path = Path(tmp)
        ruta_db = tmp_path / "medicion.db"
        ruta_uploads = tmp_path / "uploads"
        ruta_uploads.mkdir()

        cliente_id = preparar_base(ruta_db)
        puerto = puerto_libre()
        url_base = f"http://127.0.0.1:{puerto}"
        print(f"[1/4] base temporal y datos de semilla listos (cliente id={cliente_id})")

        ruta_log = tmp_path / "uvicorn.log"
        with open(ruta_log, "w", encoding="utf-8") as log:
            proceso = arrancar_api(puerto, ruta_db, ruta_uploads, log)
            try:
                esperar_listo(url_base, proceso, ruta_log)
                print(f"[2/4] API escuchando en {url_base}")

                with httpx.Client(timeout=30.0) as http:
                    token = obtener_token(url_base, http)
                    solicitudes = construir_solicitudes(url_base, token, cliente_id)
                    print(f"[3/4] midiendo latencia: {N_LATENCIA} solicitudes x {len(solicitudes)} endpoints")
                    latencia = medir_latencia(http, solicitudes, N_LATENCIA)
                    print(f"[4/4] midiendo estabilidad: {N_ESTABILIDAD} solicitudes")
                    estabilidad = medir_estabilidad(http, solicitudes, N_ESTABILIDAD)
            finally:
                proceso.terminate()
                try:
                    proceso.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proceso.kill()

    resultado = {
        "entorno": {
            "host": "127.0.0.1",
            "puerto": puerto,
            "base": "SQLite temporal (no se modifica dev.db)",
            "python": sys.version.split()[0],
            "calentamiento": "ninguno: 30 solicitudes consecutivas por endpoint",
            "conexion": "HTTP persistente (keep-alive)",
            "n_latencia": N_LATENCIA,
            "n_estabilidad": N_ESTABILIDAD,
        },
        "latencia": latencia,
        "estabilidad": estabilidad,
    }
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print(f"{'endpoint':24} {'media':>8} {'mediana':>8} {'p95':>8} {'min':>8} {'max':>8} {'cv%':>7}")
    for clave, s in latencia.items():
        print(
            f"{clave:24} {s['media']:8.2f} {s['mediana']:8.2f} {s['p95']:8.2f} "
            f"{s['minimo']:8.2f} {s['maximo']:8.2f} {s['cv']:7.1f}"
        )
    print()
    print(
        f"estabilidad: {estabilidad['total']} solicitudes | "
        f"2xx={estabilidad['2xx']} 4xx={estabilidad['4xx']} 5xx={estabilidad['5xx']} | "
        f"tasa 5xx = {estabilidad['tasa_5xx']:.2f} %"
    )
    print(f"escrito en {SALIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
