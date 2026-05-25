"""
Page Object para la página del carrito en sauce-demo.myshopify.com.
"""
import allure
from .base_page import BasePage


class CartPage(BasePage):
    """
    Representa la página del carrito de compras.
    URL: https://sauce-demo.myshopify.com/cart
    """

    # ── Selectores ──────────────────────────────────────────────────────────
    CART_URL = "https://sauce-demo.myshopify.com/cart"
    CART_ITEM_TITLE = "div.info h3 a"
    CART_ITEM_LINK = "a[href*='/products/']"

    def __init__(self, page):
        super().__init__(page)

    # ── Acciones ─────────────────────────────────────────────────────────────

    def open(self):
        """Navega directamente a la página del carrito."""
        with allure.step(f"Navegar al carrito: {self.CART_URL}"):
            self.navigate_to(self.CART_URL)
            self.page.wait_for_load_state("networkidle")
            self.take_screenshot("Página del carrito cargada")

    def get_cart_item_names(self) -> list[str]:
        """Retorna una lista con los nombres de todos los artículos en el carrito."""
        with allure.step("Obtener nombres de artículos en el carrito"):
            # Esperar a que el elemento esté en el DOM (puede estar oculto por CSS del drawer)
            self.page.wait_for_selector(self.CART_ITEM_TITLE, state="attached", timeout=10000)
            items = self.page.locator(self.CART_ITEM_TITLE).all()
            names = [item.inner_text().strip() for item in items]
            allure.attach(
                "\n".join(names) if names else "(carrito vacío)",
                name="Artículos en el carrito",
                attachment_type=allure.attachment_type.TEXT,
            )
            return names

    def is_product_in_cart(self, product_name: str) -> bool:
        """
        Verifica si un producto específico está en el carrito.
        Usa el texto completo del body para mayor robustez ante elementos ocultos por CSS.
        La comparación es case-insensitive.
        """
        with allure.step(f"Verificar que '{product_name}' está en el carrito"):
            try:
                body_text = self.page.locator("body").inner_text()
                found = product_name.lower() in body_text.lower()
                allure.attach(
                    f"Buscando: '{product_name}'\nResultado: {'✅ Encontrado' if found else '❌ No encontrado'}",
                    name="Resultado de verificación",
                    attachment_type=allure.attachment_type.TEXT,
                )
                self.take_screenshot(
                    "Carrito con producto" if found else "Carrito — producto NO encontrado"
                )
                return found
            except Exception as e:
                self.take_screenshot_on_failure("Error al verificar carrito")
                allure.attach(
                    str(e),
                    name="Error en verificación",
                    attachment_type=allure.attachment_type.TEXT,
                )
                return False
