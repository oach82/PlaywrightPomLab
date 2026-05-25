"""
Base Page Object - contiene métodos comunes para todas las páginas.
Incluye utilidades de captura de pantalla para evidencias en Allure.
"""
import allure


class BasePage:
    """Clase base para todos los Page Objects."""

    def __init__(self, page):
        self.page = page

    def navigate_to(self, url: str):
        """Navega a una URL específica."""
        self.page.goto(url)

    def get_title(self) -> str:
        """Retorna el título de la página actual."""
        return self.page.title()

    def wait_for_selector(self, selector: str, timeout: int = 10000):
        """Espera a que un selector esté visible."""
        self.page.wait_for_selector(selector, timeout=timeout)

    def take_screenshot(self, name: str = "screenshot"):
        """
        Toma una captura de pantalla y la adjunta al reporte Allure.

        Args:
            name: Nombre descriptivo que aparecerá en el reporte.
        """
        screenshot_bytes = self.page.screenshot(full_page=True)
        allure.attach(
            screenshot_bytes,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )

    def take_screenshot_on_failure(self, step_name: str = "Fallo"):
        """
        Toma una captura de pantalla de evidencia de fallo.
        Útil para llamar desde bloques except.
        """
        try:
            screenshot_bytes = self.page.screenshot(full_page=True)
            allure.attach(
                screenshot_bytes,
                name=f"FALLO — {step_name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass  # No interrumpir el flujo si la captura falla
