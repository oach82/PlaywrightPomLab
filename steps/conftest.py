"""
Configuración de pytest-bdd y Playwright.
Define los fixtures compartidos entre todos los steps.
Incluye captura automática de pantalla en fallos para evidencias en Allure.
"""
import allure
import pytest
from playwright.sync_api import sync_playwright

from pages.product_page import ProductPage
from pages.cart_page import CartPage


# ── Fixtures de Playwright ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_instance():
    """Inicia el navegador una sola vez por sesión de pruebas."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, slow_mo=400)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser_instance):
    """
    Crea un contexto y página nuevos para cada escenario.
    Captura pantalla automáticamente si el test falla.
    """
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-GB",
    )
    page = context.new_page()

    yield page

    # ── Captura de pantalla automática en fallo ───────────────────────────
    # Se ejecuta después del test; si falló, adjunta la evidencia a Allure
    if hasattr(page, "_playwright") is False:
        try:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="Captura final del escenario",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass

    context.close()


@pytest.fixture(scope="function")
def product_page(page):
    """Fixture que expone el ProductPage usando la página compartida."""
    return ProductPage(page)


@pytest.fixture(scope="function")
def cart_page(page):
    """
    Fixture que expone el CartPage usando la MISMA página compartida.
    Garantiza que el estado del carrito (cookies/sesión) se preserve
    entre el paso de agregar al carrito y la verificación.
    """
    return CartPage(page)


# ── Hook: captura de pantalla automática en cualquier fallo ──────────────────

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook de pytest que intercepta el resultado de cada test.
    Si el test falla, adjunta una captura de pantalla a Allure.
    """
    outcome = yield
    report = outcome.get_result()

    # Solo actuar en la fase 'call' (ejecución del test) y si falló
    if report.when == "call" and report.failed:
        # Intentar obtener la fixture 'page' del test actual
        page_fixture = item.funcargs.get("page")
        if page_fixture is not None:
            try:
                screenshot = page_fixture.screenshot(full_page=True)
                allure.attach(
                    screenshot,
                    name="❌ Captura en fallo",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
