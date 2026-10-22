"""Analisis de los resultados con una API de IA (R7): Gemini por HTTP o un proveedor sin conexion."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from dotenv import load_dotenv

_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent

MODELOS_GEMINI = ("gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest")

PROMPT_BASE = (
    "Eres un analista de investigacion de operaciones. Analiza los resultados de un simulador de "
    "una red de centros de datos que usa programacion dinamica (ruta mas corta y mochila), "
    "optimizacion no lineal (modelo termico cubico, metodo del gradiente para ventiladores y "
    "multiplicadores de Lagrange para repartir energia) y simulacion de colas con SimPy. "
    "Responde en espanol, en texto plano sin markdown, con: 1) diagnostico breve del desempeno, "
    "2) interpretacion de las colas frente al M/M/1 de referencia, 3) tres recomendaciones concretas."
)


class ProveedorIA(ABC):
    """Interfaz para pedir un analisis de texto. El reporte PDF no sabe que proveedor usa."""

    nombre: str = "proveedor"

    @abstractmethod
    def analizar(self, resumen: str) -> str:
        raise NotImplementedError


class ProveedorSinConexion(ProveedorIA):
    """Null Object: se usa cuando no hay clave o no hay red; el PDF se genera igual."""

    nombre = "sin conexion"

    def __init__(self, motivo: str = "no hay GEMINI_API_KEY configurada") -> None:
        self.motivo = motivo

    def analizar(self, resumen: str) -> str:
        return f"Analisis de IA no disponible ({self.motivo})."


class ClienteGemini(ProveedorIA):
    """Llamada REST a Google Gemini (mismo esquema que tarea3). Prueba varios modelos en orden."""

    nombre = "Google Gemini"

    def __init__(self, api_key: str, timeout: float = 60.0) -> None:
        self._api_key = api_key
        self._timeout = timeout

    def analizar(self, resumen: str) -> str:
        payload = {
            "contents": [{"parts": [{"text": f"{PROMPT_BASE}\n\nResultados:\n{resumen}"}]}],
            "generationConfig": {"temperature": 0.35, "maxOutputTokens": 1500},
        }
        ultimo_error = "sin respuesta"
        for modelo in MODELOS_GEMINI:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
            try:
                resp = requests.post(url, json=payload, headers={"x-goog-api-key": self._api_key}, timeout=self._timeout)
            except requests.RequestException as e:
                ultimo_error = f"error de red: {e.__class__.__name__}"
                continue
            if resp.status_code == 200:
                partes = resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
                texto = "".join(p.get("text", "") for p in partes).strip()
                if texto:
                    return texto
                ultimo_error = f"{modelo}: respuesta vacia"
            else:
                ultimo_error = f"{modelo}: HTTP {resp.status_code}"
                if resp.status_code in (401, 403):
                    break  # clave invalida: no tiene sentido probar otro modelo
        return ProveedorSinConexion(f"Gemini fallo, {ultimo_error}").analizar(resumen)


def crear_proveedor() -> ProveedorIA:
    """Lee GEMINI_API_KEY de proyecto_final/.env, del .env de la raiz del repo o del entorno."""
    for ruta in (_RAIZ_PROYECTO / ".env", _RAIZ_PROYECTO.parent / ".env"):
        if ruta.exists():
            load_dotenv(ruta, override=False)
    clave = os.environ.get("GEMINI_API_KEY", "").strip()
    return ClienteGemini(clave) if clave else ProveedorSinConexion()
