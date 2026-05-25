"""
Page Object para la página de detalle de producto en sauce-demo.myshopify.com.
"""
import allure
from .base_page import BasePage


class ProductPage(BasePage):
    """
    Representa la página de detalle de un producto.
    URL base: https://sauce-demo.myshopify.com
    """

    # ── Selectores ──────────────────────────────────────────────────────────
    PRODUCT_TITLE = "h1[itemprop='name']"
    PRODUCT_PRICE = "span.product-price"
    ADD_TO_CART_BUTTON = "input#add"
    CART_COUNT = "div#cart-animation"

    # URL del producto específico
    PRODUCT_URL = "https://sauce-demo.myshopify.com/products/grey-jacket"

    def __init__(self, page):
        super().__init__(page)

    # ── Acciones ─────────────────────────────────────────────────────────────

    def open(self):
        """Navega directamente a la página del producto Grey jacket."""
        with allure.step(f"Navegar a la página del producto: {self.PRODUCT_URL}"):
            self.navigate_to(self.PRODUCT_URL)
            self.page.wait_for_load_state("networkidle")
            self.take_screenshot("Página del producto cargada")

    def get_product_title(self) -> str:
        """Retorna el título del producto visible en la página."""
        with allure.step("Obtener el título del producto"):
            self.wait_for_selector(self.PRODUCT_TITLE)
            title = self.page.locator(self.PRODUCT_TITLE).first.inner_text().strip()
            allure.attach(
                title,
                name="Título obtenido",
                attachment_type=allure.attachment_type.TEXT,
            )
            return title

    def get_product_price(self) -> str:
        """Retorna el precio del producto visible en la página."""
        with allure.step("Obtener el precio del producto"):
            self.wait_for_selector(self.PRODUCT_PRICE)
            price = self.page.locator(self.PRODUCT_PRICE).first.inner_text().strip()
            allure.attach(
                price,
                name="Precio obtenido",
                attachment_type=allure.attachment_type.TEXT,
            )
            return price

    def add_to_cart(self):
        """Hace clic en el botón 'Agregar al carrito'."""
        with allure.step("Hacer clic en 'Add to Cart'"):
            self.wait_for_selector(self.ADD_TO_CART_BUTTON)
            self.take_screenshot("Antes de agregar al carrito")
            self.page.locator(self.ADD_TO_CART_BUTTON).click()
            self.page.wait_for_timeout(1500)
            self.take_screenshot("Después de agregar al carrito")

    def get_cart_count(self) -> int:
        """Retorna la cantidad de artículos en el carrito (ícono del header)."""
        try:
            self.wait_for_selector(self.CART_COUNT, timeout=5000)
            count_text = self.page.locator(self.CART_COUNT).first.inner_text().strip()
            return int(count_text)
        except Exception:
            return 0
