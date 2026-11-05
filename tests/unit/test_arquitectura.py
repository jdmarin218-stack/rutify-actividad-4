"""
Chequeo automático de arquitectura.

Revisa los imports de cada capa y falla si alguna depende de algo que
no debería. Es la forma de que la regla "el dominio no sabe nada de la
base de datos ni de la web" no dependa de que alguien se acuerde de ella.
"""
import ast
from pathlib import Path

RAIZ_APP = Path(__file__).resolve().parents[2] / "app"

# lo que NO puede importar cada capa
PROHIBIDO_EN_DOMINIO = ("app.infrastructure", "app.api", "app.application", "sqlalchemy", "fastapi", "pydantic")
PROHIBIDO_EN_APLICACION = ("app.infrastructure", "app.api", "sqlalchemy", "fastapi")


def _imports_de(capa: str) -> list[tuple[str, str]]:
    """Devuelve pares (archivo, modulo_importado) de todos los .py de una capa."""
    archivos = list((RAIZ_APP / capa).rglob("*.py"))
    assert archivos, f"No encontré archivos en app/{capa}; revisa la ruta"

    encontrados = []
    for archivo in archivos:
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    encontrados.append((archivo.name, alias.name))
            elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                encontrados.append((archivo.name, nodo.module))
    return encontrados


def _violaciones(capa: str, prohibidos: tuple[str, ...]) -> list[str]:
    return [
        f"{archivo} importa {modulo}"
        for archivo, modulo in _imports_de(capa)
        if modulo.startswith(prohibidos)
    ]


def test_el_dominio_no_depende_de_otras_capas_ni_de_frameworks():
    assert _violaciones("domain", PROHIBIDO_EN_DOMINIO) == []


def test_la_aplicacion_no_depende_de_infraestructura_ni_de_frameworks():
    assert _violaciones("application", PROHIBIDO_EN_APLICACION) == []