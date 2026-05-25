# Guía: Cómo agregar un nuevo escenario de prueba

Este documento explica paso a paso cómo extender el proyecto `playwrightpomlab`
con un nuevo escenario de automatización, siguiendo la arquitectura existente:
**Gherkin → Step Definitions → Page Object Model → Allure**.

---

## Índice

1. [Arquitectura del proyecto](#1-arquitectura-del-proyecto)
2. [Paso 1 — Escribir el escenario en el archivo .feature](#2-paso-1--escribir-el-escenario-en-el-archivo-feature)
3. [Paso 2 — Agregar métodos al Page Object](#3-paso-2--agregar-métodos-al-page-object)
4. [Paso 3 — Crear un nuevo Page Object (si aplica)](#4-paso-3--crear-un-nuevo-page-object-si-aplica)
5. [Paso 4 — Implementar los step definitions](#5-paso-4--implementar-los-step-definitions)
6. [Paso 5 — Ejecutar y verificar](#6-paso-5--ejecutar-y-verificar)
7. [Ejemplo completo: Eliminar un artículo del carrito](#7-ejemplo-completo-eliminar-un-artículo-del-carrito)
8. [Referencia rápida de decoradores Allure](#8-referencia-rápida-de-decoradores-allure)
9. [Errores frecuentes](#9-errores-frecuentes)

---

## 1. Arquitectura del proyecto

Antes de agregar un escenario, es importante entender cómo fluye la información:

```
features/
  └── *.feature          ← Escenarios en lenguaje Gherkin (español)
          │
          ▼
steps/
  └── test_*.py          ← Step definitions: mapean pasos Gherkin a Python
          │
          ▼
pages/
  ├── base_page.py       ← Métodos comunes (navegación, capturas)
  ├── product_page.py    ← Acciones sobre la página de producto
  └── cart_page.py       ← Acciones sobre el carrito
          │
          ▼
allure-results/          ← Evidencias PNG + resultados JSON para el reporte
```

**Regla de oro:** cada capa tiene una responsabilidad única.
- El `.feature` describe el **qué** (comportamiento esperado).
- El step definition describe el **cuándo** (mapeo de pasos).
- El Page Object describe el **cómo** (interacción con el navegador).

---

## 2. Paso 1 — Escribir el escenario en el archivo .feature

Los escenarios se escriben en `features/agregar_articulo_carrito.feature`
usando sintaxis Gherkin en español.

### Estructura de un escenario

```gherkin
Scenario: <Nombre descriptivo del escenario>
  Given <precondición>
  When  <acción del usuario>
  Then  <resultado esperado>
  And   <resultado adicional>
```

### Palabras clave disponibles

| Palabra clave | Uso |
|---------------|-----|
| `Given`       | Precondición o estado inicial |
| `When`        | Acción que ejecuta el usuario |
| `Then`        | Resultado o verificación esperada |
| `And`         | Continúa el paso anterior (Given/When/Then) |
| `But`         | Resultado negativo o excepción |
| `Background`  | Pasos comunes a todos los escenarios del feature |

### Parámetros en los pasos

Los valores entre comillas dobles se convierten en parámetros que pytest-bdd
inyecta automáticamente en el step definition:

```gherkin
Then el título del producto debe ser "Grey jacket"
#                                     ^^^^^^^^^^^^
#                                     → parámetro: expected_title = "Grey jacket"
```

### Ejemplo: agregar un nuevo escenario al .feature existente

Abre `features/agregar_articulo_carrito.feature` y añade el nuevo escenario
al final del archivo, respetando la indentación de 2 espacios:

```gherkin
# language: es
Feature: Agregar artículo al carrito
  Como cliente de Sauce Demo
  Quiero agregar un artículo al carrito
  Para poder comprarlo

  Background:
    Given que estoy en la página del producto "Grey jacket"

  Scenario: Verificar título y precio del producto
    Then el título del producto debe ser "Grey jacket"
    And el precio del producto debe ser "£55.00"

  Scenario: Agregar un artículo al carrito y verificarlo
    When agrego el producto al carrito
    Then el producto "Grey jacket" debe aparecer en el carrito

  # ── NUEVO ESCENARIO ──────────────────────────────────────────────────────
  Scenario: Eliminar un artículo del carrito
    When agrego el producto al carrito
    And elimino el producto del carrito
    Then el carrito debe estar vacío
```

> **Tip:** Si el nuevo escenario no comparte el `Background` existente
> (por ejemplo, prueba una página diferente), crea un archivo `.feature`
> separado en la misma carpeta `features/`.

---

## 3. Paso 2 — Agregar métodos al Page Object

Si el nuevo escenario necesita interactuar con elementos que ya existen en
un Page Object, agrega los métodos ahí. Si necesita una página completamente
nueva, ve al [Paso 3](#4-paso-3--crear-un-nuevo-page-object-si-aplica).

### Estructura de un método en el Page Object

Cada método debe:
1. Envolver su lógica en `with allure.step("descripción")` para que aparezca
   como sub-paso en el reporte.
2. Llamar a `self.take_screenshot("nombre")` en los momentos clave.
3. Adjuntar datos relevantes con `allure.attach(...)` cuando sea útil.

```python
# pages/cart_page.py

def remove_first_item(self):
    """Elimina el primer artículo del carrito haciendo clic en 'x'."""
    with allure.step("Eliminar el primer artículo del carrito"):
        self.wait_for_selector(self.REMOVE_BUTTON)
        self.take_screenshot("Antes de eliminar artículo")
        self.page.locator(self.REMOVE_BUTTON).first.click()
        self.page.wait_for_timeout(1000)
        self.take_screenshot("Después de eliminar artículo")

def is_cart_empty(self) -> bool:
    """Verifica si el carrito está vacío."""
    with allure.step("Verificar si el carrito está vacío"):
        body_text = self.page.locator("body").inner_text()
        empty = "your cart is empty" in body_text.lower()
        allure.attach(
            f"Carrito vacío: {'✅ Sí' if empty else '❌ No'}",
            name="Estado del carrito",
            attachment_type=allure.attachment_type.TEXT,
        )
        self.take_screenshot("Estado final del carrito")
        return empty
```

### Agregar selectores nuevos

Los selectores CSS se declaran como constantes de clase al inicio del Page Object,
antes de `__init__`. Esto facilita su mantenimiento:

```python
class CartPage(BasePage):

    # ── Selectores ──────────────────────────────────────────────────────────
    CART_URL        = "https://sauce-demo.myshopify.com/cart"
    CART_ITEM_TITLE = "div.info h3 a"
    CART_ITEM_LINK  = "a[href*='/products/']"
    REMOVE_BUTTON   = "a.remove"          # ← selector nuevo
```

> **Cómo encontrar un selector:** abre Chrome DevTools (F12), selecciona el
> elemento con el inspector y copia su selector CSS o atributo `id`/`class`.

---

## 4. Paso 3 — Crear un nuevo Page Object (si aplica)

Si el escenario cubre una página que aún no tiene Page Object (por ejemplo,
la página de checkout), crea un archivo nuevo en `pages/`.

### Plantilla base

```python
# pages/checkout_page.py
"""
Page Object para la página de checkout en sauce-demo.myshopify.com.
"""
import allure
from .base_page import BasePage


class CheckoutPage(BasePage):
    """Representa la página de checkout."""

    # ── Selectores ──────────────────────────────────────────────────────────
    CHECKOUT_URL    = "https://sauce-demo.myshopify.com/checkout"
    EMAIL_FIELD     = "input#checkout_email"
    CONTINUE_BUTTON = "button#continue_button"

    def __init__(self, page):
        super().__init__(page)

    def open(self):
        """Navega a la página de checkout."""
        with allure.step(f"Navegar a checkout: {self.CHECKOUT_URL}"):
            self.navigate_to(self.CHECKOUT_URL)
            self.page.wait_for_load_state("networkidle")
            self.take_screenshot("Página de checkout cargada")

    def fill_email(self, email: str):
        """Ingresa el email en el formulario de checkout."""
        with allure.step(f"Ingresar email: {email}"):
            self.wait_for_selector(self.EMAIL_FIELD)
            self.page.locator(self.EMAIL_FIELD).fill(email)
            self.take_screenshot("Email ingresado")
```

### Registrar el nuevo Page Object

Agrega la importación y exportación en `pages/__init__.py`:

```python
# pages/__init__.py
from .base_page import BasePage
from .product_page import ProductPage
from .cart_page import CartPage
from .checkout_page import CheckoutPage          # ← agregar

__all__ = ["BasePage", "ProductPage", "CartPage", "CheckoutPage"]
```

### Agregar el fixture en `steps/conftest.py`

Para que pytest-bdd pueda inyectar el nuevo Page Object en los steps,
agrega un fixture en `steps/conftest.py`:

```python
# steps/conftest.py

from pages.checkout_page import CheckoutPage     # ← importar

@pytest.fixture(scope="function")
def checkout_page(page):
    """Fixture que expone el CheckoutPage usando la página compartida."""
    return CheckoutPage(page)
```

---

## 5. Paso 4 — Implementar los step definitions

Los step definitions conectan los pasos Gherkin con los métodos del Page Object.
Pueden ir en el archivo de steps existente o en uno nuevo.

### Cuándo crear un archivo de steps nuevo

Crea `steps/test_<nombre_feature>.py` cuando el nuevo escenario pertenece a
una funcionalidad diferente (por ejemplo, `test_checkout.py` para flujos de pago).
Si el escenario extiende la feature actual, agrégalo al archivo existente.

### Estructura de un step definition

```python
# steps/test_agregar_articulo_carrito.py

@allure.feature("Carrito de compras")          # Agrupa en el reporte
@allure.story("Eliminar producto del carrito") # Sub-agrupación
@allure.severity(allure.severity_level.CRITICAL)
@when("elimino el producto del carrito")
def remove_product_from_cart(cart_page: CartPage, product_page: ProductPage):
    """Elimina el primer artículo del carrito."""
    with allure.step("Eliminar artículo del carrito"):
        cart_page.page = product_page.page     # compartir sesión
        cart_page.open()
        cart_page.remove_first_item()


@allure.feature("Carrito de compras")
@allure.story("Eliminar producto del carrito")
@allure.severity(allure.severity_level.CRITICAL)
@then("el carrito debe estar vacío")
def verify_cart_is_empty(cart_page: CartPage, product_page: ProductPage):
    """Verifica que el carrito no tenga artículos."""
    with allure.step("Verificar que el carrito está vacío"):
        cart_page.page = product_page.page
        assert cart_page.is_cart_empty(), "El carrito debería estar vacío pero contiene artículos."
```

### Reglas de mapeo Gherkin → Python

| Gherkin | Decorador Python |
|---------|-----------------|
| `Given` | `@given(...)` |
| `When`  | `@when(...)` |
| `Then`  | `@then(...)` |
| `And` / `But` | Reutiliza el decorador del paso anterior |

### Parámetros con `parsers.parse`

Cuando el paso tiene valores entre comillas, usa `parsers.parse`:

```python
# Gherkin:  Then el precio debe ser "£55.00"
@then(parsers.parse('el precio debe ser "{expected_price}"'))
def verify_price(product_page: ProductPage, expected_price: str):
    ...
```

### Cargar los escenarios del .feature

Si creas un archivo de steps nuevo, asegúrate de incluir la línea `scenarios()`
al inicio para que pytest-bdd descubra los escenarios:

```python
# Al inicio del archivo de steps
scenarios("../features/agregar_articulo_carrito.feature")
```

Si creas un `.feature` nuevo, apunta a ese archivo:

```python
scenarios("../features/mi_nueva_feature.feature")
```

---

## 6. Paso 5 — Ejecutar y verificar

### Ejecutar todos los tests

```cmd
cd playwrightpomlab
pytest -v
```

### Ejecutar solo el nuevo escenario por nombre

```cmd
pytest -v -k "Eliminar un artículo"
```

### Ejecutar y generar reporte Allure

```cmd
pytest -v --alluredir=allure-results --clean-alluredir
allure serve allure-results
```

### Verificar que el nuevo escenario aparece en el reporte

En el reporte Allure, el nuevo escenario debe aparecer:
- En la sección **Suites** bajo el nombre del archivo de steps.
- En la sección **Features** bajo el `@allure.feature` que le asignaste.
- Con sus capturas de pantalla en la pestaña **Attachments** de cada paso.

---

## 7. Ejemplo completo: Eliminar un artículo del carrito

Este ejemplo muestra todos los archivos modificados para agregar el escenario
"Eliminar un artículo del carrito".

### 7.1 — Archivo .feature

```gherkin
# features/agregar_articulo_carrito.feature

  Scenario: Eliminar un artículo del carrito
    When agrego el producto al carrito
    And elimino el producto del carrito
    Then el carrito debe estar vacío
```

### 7.2 — Selector nuevo en CartPage

```python
# pages/cart_page.py  →  sección de selectores

REMOVE_BUTTON = "a.remove"
```

### 7.3 — Métodos nuevos en CartPage

```python
# pages/cart_page.py

def remove_first_item(self):
    """Elimina el primer artículo del carrito."""
    with allure.step("Eliminar el primer artículo del carrito"):
        self.wait_for_selector(self.REMOVE_BUTTON)
        self.take_screenshot("Antes de eliminar artículo")
        self.page.locator(self.REMOVE_BUTTON).first.click()
        self.page.wait_for_timeout(1000)
        self.take_screenshot("Después de eliminar artículo")

def is_cart_empty(self) -> bool:
    """Verifica si el carrito está vacío."""
    with allure.step("Verificar si el carrito está vacío"):
        body_text = self.page.locator("body").inner_text()
        empty = "your cart is empty" in body_text.lower()
        allure.attach(
            f"Carrito vacío: {'✅ Sí' if empty else '❌ No'}",
            name="Estado del carrito",
            attachment_type=allure.attachment_type.TEXT,
        )
        self.take_screenshot("Estado final del carrito")
        return empty
```

### 7.4 — Step definitions nuevos

```python
# steps/test_agregar_articulo_carrito.py

@allure.feature("Carrito de compras")
@allure.story("Eliminar producto del carrito")
@allure.severity(allure.severity_level.CRITICAL)
@when("elimino el producto del carrito")
def remove_product_from_cart(cart_page: CartPage, product_page: ProductPage):
    """Elimina el primer artículo del carrito."""
    with allure.step("Eliminar artículo del carrito"):
        cart_page.page = product_page.page
        cart_page.open()
        cart_page.remove_first_item()


@allure.feature("Carrito de compras")
@allure.story("Eliminar producto del carrito")
@allure.severity(allure.severity_level.CRITICAL)
@then("el carrito debe estar vacío")
def verify_cart_is_empty(cart_page: CartPage, product_page: ProductPage):
    """Verifica que el carrito no tenga artículos."""
    with allure.step("Verificar que el carrito está vacío"):
        cart_page.page = product_page.page
        assert cart_page.is_cart_empty(), (
            "El carrito debería estar vacío pero contiene artículos."
        )
```

### 7.5 — Resultado esperado en Allure

```
Suites
  └── test_agregar_articulo_carrito
        ├── ✅ test_verificar_título_y_precio_del_producto
        ├── ✅ test_agregar_un_artículo_al_carrito_y_verificarlo
        └── ✅ test_eliminar_un_artículo_del_carrito          ← nuevo
              ├── Step: Abrir la página del producto 'Grey jacket'
              │     └── 📷 Página del producto cargada
              ├── Step: Hacer clic en el botón 'Add to Cart'
              │     ├── 📷 Antes de agregar al carrito
              │     └── 📷 Después de agregar al carrito
              ├── Step: Eliminar artículo del carrito
              │     ├── 📷 Antes de eliminar artículo
              │     └── 📷 Después de eliminar artículo
              └── Step: Verificar que el carrito está vacío
                    ├── 📄 Estado del carrito
                    └── 📷 Estado final del carrito
```

---

## 8. Referencia rápida de decoradores Allure

```python
@allure.feature("Nombre del módulo")          # Agrupa tests por funcionalidad
@allure.story("Nombre del flujo")             # Sub-agrupación dentro del feature
@allure.title("Título legible del test")      # Nombre que aparece en el reporte
@allure.description("Descripción detallada") # Texto explicativo del test
@allure.severity(allure.severity_level.BLOCKER)   # Máxima prioridad
@allure.severity(allure.severity_level.CRITICAL)  # Alta prioridad
@allure.severity(allure.severity_level.NORMAL)    # Prioridad media
@allure.severity(allure.severity_level.MINOR)     # Baja prioridad
@allure.severity(allure.severity_level.TRIVIAL)   # Mínima prioridad
@allure.tag("regresión", "smoke")             # Etiquetas libres
@allure.link("https://jira.empresa.com/PROJ-123", name="Ticket")  # Enlace externo
```

### Adjuntar evidencias manualmente dentro de un step

```python
# Captura de pantalla
self.take_screenshot("Nombre descriptivo")

# Texto plano
allure.attach("contenido", name="Nombre", attachment_type=allure.attachment_type.TEXT)

# HTML
allure.attach("<b>html</b>", name="Nombre", attachment_type=allure.attachment_type.HTML)

# JSON
import json
allure.attach(json.dumps(data, indent=2), name="Datos", attachment_type=allure.attachment_type.JSON)
```

---

## 9. Errores frecuentes

### `StepDefinitionNotFoundError`
El paso Gherkin no tiene un step definition que lo mapee.

**Solución:** verifica que el texto del paso en el `.feature` coincida
exactamente (incluyendo mayúsculas y comillas) con el string del decorador
`@given/@when/@then` en el archivo de steps.

---

### `fixture 'mi_fixture' not found`
El step definition usa un Page Object que no tiene fixture registrado.

**Solución:** agrega el fixture correspondiente en `steps/conftest.py`:
```python
@pytest.fixture(scope="function")
def mi_page(page):
    return MiPage(page)
```

---

### `TimeoutError: waiting for locator(...) to be visible`
El selector CSS no encuentra el elemento o el elemento está oculto.

**Solución:**
1. Abre Chrome DevTools (F12) en la página bajo prueba.
2. Usa el inspector para identificar el selector correcto.
3. Prueba el selector en la consola: `document.querySelector("tu-selector")`.
4. Si el elemento existe pero está oculto, usa `state="attached"` en lugar
   de `state="visible"` en `wait_for_selector`.

---

### El escenario no aparece en el reporte Allure
El archivo `.feature` no está siendo cargado por el archivo de steps.

**Solución:** verifica que la ruta en `scenarios(...)` sea correcta:
```python
# Desde steps/, la ruta relativa a features/ es ../features/
scenarios("../features/mi_feature.feature")
```

---

### Dos escenarios comparten un paso pero con comportamiento diferente
Usa parámetros en el paso para diferenciarlos:

```gherkin
# En lugar de dos pasos distintos:
Then el carrito debe tener 1 artículo
Then el carrito debe tener 2 artículos

# Usa un paso parametrizado:
Then el carrito debe tener "1" artículo
Then el carrito debe tener "2" artículos
```

```python
@then(parsers.parse('el carrito debe tener "{cantidad}" artículo'))
def verify_cart_count(cart_page: CartPage, product_page: ProductPage, cantidad: str):
    cart_page.page = product_page.page
    assert cart_page.get_cart_count() == int(cantidad)
```
