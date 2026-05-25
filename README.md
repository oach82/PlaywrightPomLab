# playwrightpomlab

Proyecto de automatización de pruebas E2E con **Python + Playwright** bajo el patrón **Page Object Model (POM)**, usando **pytest-bdd** para escenarios Gherkin y **Allure** como reporteador.

---

## Estructura del proyecto

```
playwrightpomlab/
├── features/
│   └── agregar_articulo_carrito.feature   # Escenarios BDD en Gherkin
├── pages/
│   ├── __init__.py
│   ├── base_page.py                       # Clase base con métodos comunes
│   ├── product_page.py                    # POM: página de detalle de producto
│   └── cart_page.py                       # POM: página del carrito
├── steps/
│   ├── __init__.py
│   ├── conftest.py                        # Fixtures de Playwright y páginas
│   └── test_agregar_articulo_carrito.py   # Step definitions pytest-bdd
├── allure-results/                        # Resultados generados por Allure
├── reports/                               # Reporte HTML de Allure
├── conftest.py                            # Configuración raíz de pytest
├── pytest.ini                             # Configuración de pytest
├── requirements.txt                       # Dependencias Python
├── build.gradle                           # Tareas Gradle para orquestar el proyecto
├── settings.gradle                        # Nombre del proyecto Gradle
└── README.md
```

---

## Requisitos previos

| Herramienta | Versión mínima | Instalación |
|-------------|---------------|-------------|
| Python      | 3.11+         | [python.org](https://www.python.org/downloads/) |
| pip         | 23+           | Incluido con Python |
| Gradle      | 8.x           | [gradle.org](https://gradle.org/install/) o `choco install gradle` |
| Allure CLI  | 2.27+         | [allure-framework.org](https://allurereport.org/docs/install/) o `choco install allure` |
| Java JDK    | 11+           | Requerido por Gradle y Allure CLI |

> **Windows**: se recomienda instalar Allure con Scoop o Chocolatey:
> ```cmd
> choco install allure
> ```

---

## Instalación y configuración

### Opción A — Con Gradle (recomendado)

Gradle orquesta todo el flujo automáticamente.

```cmd
cd playwrightpomlab

:: Instalar dependencias Python + navegadores Playwright
gradle installBrowsers

:: Ejecutar tests y generar reporte Allure
gradle runAll
```

### Opción B — Manual con pip y pytest

**1. Crear y activar entorno virtual (opcional pero recomendado)**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**2. Instalar dependencias Python**

```cmd
pip install -r requirements.txt
```

**3. Instalar los navegadores de Playwright**

```cmd
python -m playwright install chromium
```

---

## Ejecución de los tests

### Ejecutar todos los escenarios

```cmd
cd playwrightpomlab
pytest -v
```

### Ejecutar con reporte Allure (resultados)

```cmd
pytest -v --alluredir=allure-results --clean-alluredir
```

### Ejecutar un escenario específico por nombre

```cmd
pytest -v -k "Verificar título"
```

### Ejecutar en modo headless (sin abrir el navegador)

Edita `steps/conftest.py` y cambia:
```python
browser = playwright.chromium.launch(headless=True)
```

---

## Generación del reporte Allure

### Generar reporte HTML estático

```cmd
allure generate allure-results --output reports/allure-report --clean
```

### Abrir el reporte en el navegador

```cmd
allure open reports/allure-report
```

### Generar y abrir en un solo comando (servidor temporal)

```cmd
allure serve allure-results
```

---

## Evidencias y capturas de pantalla

El proyecto captura pantallas automáticamente en los siguientes momentos:

| Momento | Descripción |
|---------|-------------|
| Página del producto cargada | Al abrir la URL del producto |
| Antes de agregar al carrito | Justo antes del clic en "Add to Cart" |
| Después de agregar al carrito | Confirmación visual del clic |
| Título del producto verificado | Al validar el título |
| Precio del producto verificado | Al validar el precio |
| Página del carrito cargada | Al navegar al carrito |
| Carrito con producto | Al confirmar que el producto está en el carrito |
| ❌ Captura en fallo | Automática si cualquier step falla |

Todas las capturas se adjuntan directamente al reporte Allure como attachments PNG.

El reporte también incluye:
- **Sección Environment**: versión de Python, OS, navegador y URL base
- **Categorías de fallos**: clasificación automática por tipo de error
- **Pasos detallados**: cada acción del POM aparece como un sub-paso en Allure
- **Attachments de texto**: valores esperados vs obtenidos en cada aserción

---

## Tareas Gradle disponibles

| Tarea              | Descripción                                              |
|--------------------|----------------------------------------------------------|
| `gradle installDeps`     | Instala dependencias de `requirements.txt`         |
| `gradle installBrowsers` | Instala Chromium para Playwright                   |
| `gradle test`            | Ejecuta los tests y genera `allure-results`        |
| `gradle allureReport`    | Genera el reporte HTML en `reports/allure-report`  |
| `gradle allureServe`     | Abre el reporte en el navegador (servidor temporal)|
| `gradle runAll`          | Flujo completo: instalar → tests → reporte         |
| `gradle cleanResults`    | Elimina `allure-results` y `reports`               |

---

## Escenarios cubiertos

**Feature:** Agregar artículo al carrito  
**URL bajo prueba:** https://sauce-demo.myshopify.com/products/grey-jacket

| Escenario | Descripción |
|-----------|-------------|
| Verificar título y precio del producto | Valida que el título sea "Grey jacket" y el precio "£55.00" |
| Agregar un artículo al carrito y verificarlo | Agrega el producto al carrito y confirma que aparece en él |

---

## Tecnologías utilizadas

- **[Playwright](https://playwright.dev/python/)** — automatización del navegador
- **[pytest](https://docs.pytest.org/)** — framework de testing
- **[pytest-bdd](https://pytest-bdd.readthedocs.io/)** — integración Gherkin/BDD
- **[Allure](https://allurereport.org/)** — reporteador de resultados
- **[Gradle](https://gradle.org/)** — orquestación de tareas de build

---

## Solución de problemas

**Error: `allure` no se reconoce como comando**  
→ Instala Allure CLI y asegúrate de que esté en el PATH del sistema.

**Error: `playwright install` falla**  
→ Ejecuta `python -m playwright install --with-deps chromium` para instalar dependencias del sistema.

**Los tests fallan con `TimeoutError`**  
→ La tienda puede estar en mantenimiento. Verifica que https://sauce-demo.myshopify.com esté accesible.

**Error de importación de `pages`**  
→ Asegúrate de ejecutar `pytest` desde el directorio `playwrightpomlab/` donde está el `conftest.py` raíz.
