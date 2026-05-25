"""
Step definitions para la feature: Agregar artículo al carrito.
Usa pytest-bdd para mapear los pasos Gherkin a código Python.
Incluye decoradores Allure para enriquecer el reporte.
"""
import allure
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from pages.product_page import ProductPage
from pages.cart_page import CartPage

# ── Cargar todos los escenarios del archivo .feature ─────────────────────────
scenarios("../features/agregar_articulo_carrito.feature")


# ── Background ────────────────────────────────────────────────────────────────

@given(parsers.parse('que estoy en la página del producto "{product_name}"'))
def navigate_to_product(product_page: ProductPage, product_name: str):
    """Navega a la página del producto indicado."""
    with allure.step(f"Abrir la página del producto '{product_name}'"):
        product_page.open()


# ── Scenario: Verificar título y precio del producto ─────────────────────────

@allure.feature("Catálogo de productos")
@allure.story("Verificar información del producto")
@allure.severity(allure.severity_level.NORMAL)
@then(parsers.parse('el título del producto debe ser "{expected_title}"'))
def verify_product_title(product_page: ProductPage, expected_title: str):
    """Verifica que el título del producto coincida con el esperado."""
    with allure.step(f"Verificar que el título sea '{expected_title}'"):
        actual_title = product_page.get_product_title()
        allure.attach(
            f"Esperado : '{expected_title}'\nObtenido : '{actual_title}'",
            name="Comparación de título",
            attachment_type=allure.attachment_type.TEXT,
        )
        product_page.take_screenshot("Título del producto verificado")
        assert actual_title == expected_title, (
            f"Título esperado: '{expected_title}', pero se encontró: '{actual_title}'"
        )


@allure.feature("Catálogo de productos")
@allure.story("Verificar información del producto")
@allure.severity(allure.severity_level.NORMAL)
@then(parsers.parse('el precio del producto debe ser "{expected_price}"'))
def verify_product_price(product_page: ProductPage, expected_price: str):
    """Verifica que el precio del producto coincida con el esperado."""
    with allure.step(f"Verificar que el precio sea '{expected_price}'"):
        actual_price = product_page.get_product_price()
        allure.attach(
            f"Esperado : '{expected_price}'\nObtenido : '{actual_price}'",
            name="Comparación de precio",
            attachment_type=allure.attachment_type.TEXT,
        )
        product_page.take_screenshot("Precio del producto verificado")
        assert actual_price == expected_price, (
            f"Precio esperado: '{expected_price}', pero se encontró: '{actual_price}'"
        )


# ── Scenario: Agregar un artículo al carrito y verificarlo ───────────────────

@allure.feature("Carrito de compras")
@allure.story("Agregar producto al carrito")
@allure.severity(allure.severity_level.CRITICAL)
@when("agrego el producto al carrito")
def add_product_to_cart(product_page: ProductPage):
    """Hace clic en el botón 'Agregar al carrito'."""
    with allure.step("Hacer clic en el botón 'Add to Cart'"):
        product_page.add_to_cart()


@allure.feature("Carrito de compras")
@allure.story("Agregar producto al carrito")
@allure.severity(allure.severity_level.CRITICAL)
@then(parsers.parse('el producto "{product_name}" debe aparecer en el carrito'))
def verify_product_in_cart(product_page: ProductPage, cart_page: CartPage, product_name: str):
    """Navega al carrito y verifica que el producto esté presente."""
    with allure.step(f"Verificar que '{product_name}' aparece en el carrito"):
        # Compartir la misma instancia de página para preservar la sesión/cookies
        cart_page.page = product_page.page
        cart_page.open()
        assert cart_page.is_product_in_cart(product_name), (
            f"El producto '{product_name}' no se encontró en el carrito."
        )
