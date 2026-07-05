"""Generate realistic demo data for multiple product categories."""

import random
from typing import List, Dict, Any


def generate_demo_data(categoria: str = 'vinos', cantidad: int = 20, seed: int = 42) -> List[Dict[str, Any]]:
    """Generate demo products for a category.

    Args:
        categoria: Category name (vinos, electronica, indumentaria)
        cantidad: Number of products to generate
        seed: Random seed for reproducibility

    Returns:
        List of product dicts
    """
    random.seed(seed)

    if categoria == 'vinos':
        return _generar_vinos(cantidad)
    elif categoria == 'electronica':
        return _generar_electronica(cantidad)
    elif categoria == 'indumentaria':
        return _generar_indumentaria(cantidad)
    else:
        return _generar_vinos(cantidad)


def _generar_vinos(cantidad: int) -> List[Dict[str, Any]]:
    """Generate wine demo products."""
    nombres = [
        'Malbec Bodega Catena Zapata', 'Torrontés Etchart', 'Cabernet Sauvignon Achaval Ferrer',
        'Pinot Noir Chacra', 'Merlot Alamos', 'Bonarda San Telmo', 'Syrah Viña Cobos',
        'Tannat Montevidiano', 'Barbera Trapiche', 'Sauvignon Blanc Casa Crespo'
    ]

    comentarios_positivos = [
        'Excelente vino, aroma increíble y sabor muy refinado. Lo recomiendo.',
        'Impecable la calidad. De verdad es un vino de categoría. ¡Joya!',
        'Buenísimo, muy aromático y con cuerpo. Vale cada peso.',
        'Llegó en perfecto estado. El envío fue rapidísimo. Un capo el vendedor.',
        'De diez este vino. Sabor complejo y agradable. Me encanta.',
        'Fantástico. El aroma es increíble. Armonía perfecta en cada sorbo.'
    ]

    comentarios_negativos = [
        'Bastante malo. No tiene el sabor esperado. Decepcionante.',
        'Llegó dañado. El envío fue pésimo. Nunca más compro acá.',
        'Caro para la calidad que ofrece. Hay opciones mejores.',
        'Flojo. No se justifica el precio. Esperaba mucho más.',
        'Deficiente en aroma y sabor. Trucho sinceramente.',
        'Horrible, vinagre prácticamente. Un desastre total.'
    ]

    productos = []
    for i in range(cantidad):
        nombre = random.choice(nombres)
        precio = round(random.uniform(80, 500), 2)
        estrellas = random.choice([1, 2, 3, 4, 5])
        calificaciones = random.randint(5, 150)

        comentarios = []
        num_comentarios = random.randint(3, 8)
        for _ in range(num_comentarios):
            if estrellas >= 4:
                comentario = random.choice(comentarios_positivos)
            elif estrellas <= 2:
                comentario = random.choice(comentarios_negativos)
            else:
                comentario = random.choice(comentarios_positivos + comentarios_negativos)
            comentarios.append(comentario)

        productos.append({
            'nombre': f"{nombre} ({2023 - i % 5})",
            'precio': str(precio),
            'moneda': 'ARS',
            'estrellas': str(estrellas),
            'calificaciones': str(calificaciones),
            'envio': random.choice(['Gratis', 'Con costo', 'Por pagar']),
            'descuento': f"{random.randint(0, 30)}%" if random.random() > 0.6 else 'Sin descuento',
            'url': f'https://articulo.mercadolibre.com.ar/mla-{1000000 + i}',
            'id': f'mla_{1000000 + i}',
            'vendedor': f'Bodega Premium {i % 5}',
            'comentarios': comentarios
        })

    return productos


def _generar_electronica(cantidad: int) -> List[Dict[str, Any]]:
    """Generate electronics demo products."""
    nombres = [
        'Tablet Samsung Galaxy Tab', 'Smartphone Motorola Moto G50', 'Laptop ASUS VivoBook',
        'Auriculares Sony WH-CH', 'Smartwatch Xiaomi Mi Band', 'Cargador USB-C 65W',
        'Powerbank 20000mAh', 'Cable USB tipo C', 'Monitor LG 24 pulgadas', 'Teclado mecánico'
    ]

    comentarios_positivos = [
        'Excelente aparato, rápido y confiable. Muy satisfecho con la compra.',
        'Impecable la velocidad. Durable y bien diseñado. Lo recomiendo.',
        'Buenísimo por el precio. Rendimiento muy bueno. Llegó rápido.',
        'De diez este producto. Funciona perfectamente. Envío super rápido.',
        'Fantástico. Muy resistente y potente. Una gozada.',
        'Calidad premium. Excelente rendimiento. Vale la inversión.'
    ]

    comentarios_negativos = [
        'Malo. Se rompió a los dos meses. Deficiente calidad.',
        'Llegó dañado. El vendedor no responde. Desastre total.',
        'Flojo. No funciona correctamente. Caro para lo que ofrece.',
        'Horrible, no dura nada. Basura. Quiero devolverlo.',
        'Berreta sinceramente. Espera dos meses y falla. Choto.',
        'Un desastre. No reconoce la batería. Inutilizable.'
    ]

    productos = []
    for i in range(cantidad):
        nombre = random.choice(nombres)
        precio = round(random.uniform(500, 5000), 2)
        estrellas = random.choice([1, 2, 3, 4, 5])
        calificaciones = random.randint(10, 300)

        comentarios = []
        num_comentarios = random.randint(3, 8)
        for _ in range(num_comentarios):
            if estrellas >= 4:
                comentario = random.choice(comentarios_positivos)
            elif estrellas <= 2:
                comentario = random.choice(comentarios_negativos)
            else:
                comentario = random.choice(comentarios_positivos + comentarios_negativos)
            comentarios.append(comentario)

        productos.append({
            'nombre': f"{nombre} #{i + 1}",
            'precio': str(precio),
            'moneda': 'ARS',
            'estrellas': str(estrellas),
            'calificaciones': str(calificaciones),
            'envio': random.choice(['Gratis', 'Con costo']),
            'descuento': f"{random.randint(5, 50)}%" if random.random() > 0.5 else 'Sin descuento',
            'url': f'https://articulo.mercadolibre.com.ar/mla-{2000000 + i}',
            'id': f'mla_{2000000 + i}',
            'vendedor': f'Tech Store {i % 7}',
            'comentarios': comentarios
        })

    return productos


def _generar_indumentaria(cantidad: int) -> List[Dict[str, Any]]:
    """Generate clothing demo products."""
    nombres = [
        'Remera Básica Algodon', 'Pantalon Jeans Azul', 'Campera Invierno Acolchada',
        'Zapatillas Deportivas', 'Pollera Midi Estampada', 'Buzo Algodón Hoodie',
        'Musculosa Deportiva', 'Pantalon Chino Gris', 'Blazer Neuro', 'Vestido Casual'
    ]

    comentarios_positivos = [
        'Excelente tela. Muy cómodo y bien hecho. Recomendadísimo.',
        'Impecable la calidad. Ajusta perfecto. Muy conforme.',
        'Buenísimo por el precio. Tela suave y resistente. Lo volvería a comprar.',
        'De diez este producto. Quedan hermoso. Envío rapidísimo.',
        'Fantástico. Diseño moderno y cómodo. Llegó en perfecto estado.',
        'Muy bueno. Tela de calidad y durabilidad comprobada.'
    ]

    comentarios_negativos = [
        'Talle incorrecto. No queda bien. Calidad mala.',
        'Llegó desteñido. El color no es el que mostraba. Decepcionante.',
        'Flojo. Se descose al primer lavado. Durabilidad nula.',
        'Horrible. Material delgado y barato. No recomiendo.',
        'Berreta la tela. Se deforma con un lavado. Un desastre.',
        'Pésima calidad. Se rompió en una semana. Basura.'
    ]

    productos = []
    for i in range(cantidad):
        nombre = random.choice(nombres)
        precio = round(random.uniform(100, 1500), 2)
        estrellas = random.choice([1, 2, 3, 4, 5])
        calificaciones = random.randint(5, 200)

        comentarios = []
        num_comentarios = random.randint(3, 8)
        for _ in range(num_comentarios):
            if estrellas >= 4:
                comentario = random.choice(comentarios_positivos)
            elif estrellas <= 2:
                comentario = random.choice(comentarios_negativos)
            else:
                comentario = random.choice(comentarios_positivos + comentarios_negativos)
            comentarios.append(comentario)

        productos.append({
            'nombre': f"{nombre} Talle {random.choice(['XS', 'S', 'M', 'L', 'XL', 'XXL'])}",
            'precio': str(precio),
            'moneda': 'ARS',
            'estrellas': str(estrellas),
            'calificaciones': str(calificaciones),
            'envio': random.choice(['Gratis', 'Con costo']),
            'descuento': f"{random.randint(10, 40)}%" if random.random() > 0.5 else 'Sin descuento',
            'url': f'https://articulo.mercadolibre.com.ar/mla-{3000000 + i}',
            'id': f'mla_{3000000 + i}',
            'vendedor': f'Fashion Store {i % 6}',
            'comentarios': comentarios
        })

    return productos
