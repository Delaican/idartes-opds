# Catálogo OPDS 2.0 para Idartes

Este proyecto genera un catálogo [OPDS](https://opds.io/) 2.0 del repositorio de libros digitales de Idartes (Instituto Distrital de las Artes de Bogotá). El catálogo permite acceder a publicaciones en formato EPUB y PDF organizadas por área temática.

## Estructura del proyecto

El código realiza scraping del sitio web [https://idartesencasa.gov.co/libros](https://idartesencasa.gov.co/libros) para extraer información de cada libro, incluyendo su metadata y enlaces de descarga. Los datos se transforman al formato OPDS 2.0 ([JSON Schema](https://github.com/opds-community/drafts/tree/master/schema)) y se generan catálogos tanto generales como específicos por área y formato.

Los archivos JSON del catálogo OPDS ya están disponibles en el directorio `catalogs/`. No es necesario ejecutar el script de scraping si se desea utilizar estos catálogos directamente.

## Ejecución del script de scraping

Si se desea regenerar los catálogos o modificar la extracción de datos, se puede ejecutar el script siguiendo estos pasos:

Clonar el repositorio y dirigirse al directorio:

```bash
git clone https://github.com/Delaican/idartes-opds.git
cd idartes-opds
```

Crear y activar el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar el script:

```bash
python3 scraping.py
```

El script generará los archivos JSON en el directorio `catalogs/`, incluyendo un catálogo principal (`home.json`) y catálogos específicos por área temática y formato.

## Servir el catálogo

Para acceder al catálogo OPDS desde un e-reader compatible, se debe iniciar un servidor HTTP local desde el directorio del proyecto:

```bash
python3 -m http.server
```

El catálogo estará disponible en:

```
http://localhost:8000/catalogs/home.json
```

## Compatibilidad

El catálogo utiliza OPDS 2.0 (JSON Schema). En las pruebas realizadas, el único e-reader que ha sido capaz de leer este formato correctamente es Foliate. Otros lectores pueden tener problemas de compatibilidad con esta versión del estándar OPDS.
