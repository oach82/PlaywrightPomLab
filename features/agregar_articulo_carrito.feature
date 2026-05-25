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
