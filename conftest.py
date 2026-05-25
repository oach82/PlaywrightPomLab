"""
conftest.py raíz del proyecto.
- Agrega el directorio raíz al sys.path para que los imports de 'pages' funcionen.
- Genera el archivo environment.properties y categories.json para el reporte Allure.
"""
import sys
import os
import json
import platform

# Asegura que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(__file__))

# Directorio de resultados Allure
_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "allure-results")


def _write_allure_environment():
    """Escribe environment.properties en allure-results."""
    os.makedirs(_RESULTS_DIR, exist_ok=True)
    env_file = os.path.join(_RESULTS_DIR, "environment.properties")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write("Browser=Chromium\n")
        f.write("Browser.Version=125\n")
        f.write("Base.URL=https://sauce-demo.myshopify.com\n")
        f.write(f"Python.Version={platform.python_version()}\n")
        f.write(f"OS={platform.system()} {platform.release()}\n")
        f.write("Framework=pytest-bdd + Playwright\n")
        f.write("Allure.Version=2.13.5\n")


def _write_allure_categories():
    """Escribe categories.json en allure-results."""
    os.makedirs(_RESULTS_DIR, exist_ok=True)
    categories = [
        {
            "name": "Fallos de aserción",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*"
        },
        {
            "name": "Errores de timeout",
            "matchedStatuses": ["failed", "broken"],
            "messageRegex": ".*TimeoutError.*"
        },
        {
            "name": "Errores de elemento no encontrado",
            "matchedStatuses": ["broken"],
            "messageRegex": ".*wait_for_selector.*"
        },
        {
            "name": "Tests exitosos",
            "matchedStatuses": ["passed"]
        }
    ]
    categories_file = os.path.join(_RESULTS_DIR, "categories.json")
    with open(categories_file, "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)


def pytest_sessionstart(session):
    """
    Hook que se ejecuta al inicio de la sesión de pytest,
    DESPUÉS de que allure-pytest haya limpiado el directorio de resultados.
    Genera los archivos de configuración del reporte Allure.
    """
    _write_allure_environment()
    _write_allure_categories()
