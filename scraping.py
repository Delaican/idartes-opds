import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def get_soup(path):
    html_content = requests.get(path).text
    return BeautifulSoup(html_content, features="html.parser")


def get_books_url(soup):
    return [book_element.find("a").get('href') for book_element in soup.find_all('div', class_="list-info")]


def get_element_info_values(base_element, class_name):
    element = base_element.find("div", class_=class_name)
    # Verifica que el elemento existe
    if element:
        # Encuentra todos los items del elemento
        field_items = element.find_all("div", class_="field__item")
        if field_items:
            texts = [item.text.strip() for item in field_items]
            # Retorna una lista si hay más de un elemento o el valor si solo hay uno
            return texts[0] if len(texts) == 1 else texts
    return None


def get_book_data(path, book_soup):
    data = {}
    
    # Título
    data["title"] = book_soup.find("h1").text.strip()
    
    # Portada y descripción
    info_element = book_soup.find('div', class_="group-info")
    image_src = info_element.find("img").get("src")
    data["images"] = [{
        "href": f'{path}{image_src}',
        "type": "image/jpeg"
    }]
    data["description"] = info_element.text.lstrip().split("\n")[0]
    
    details_element = book_soup.find('div', class_="group-details")

    # Links de descarga
    links = []
    download_elements = details_element.find_all("a", class_="btn-download")
    for download_element in download_elements:
        download_url = download_element.get("href")
        if download_url.endswith(".pdf"):
            links.append({
                "rel": "http://opds-spec.org/acquisition/open-access",
                "href": f'{path}{download_url}',
                "type": "application/pdf"
            })
        elif download_url.endswith(".epub"):
            links.append({
                "rel": "http://opds-spec.org/acquisition/open-access",
                "href": f'{path}{download_url}',
                "type": "application/epub+zip"
            })
    
    if links:
        data["links"] = links
    
    # Campos metadata
    fields = {
        "author": get_element_info_values(details_element, "field--name-field-autor"),
        "publisher": get_element_info_values(details_element, "field--name-field-editorial"),
        "published": get_element_info_values(details_element, "field--name-field-year"),
        "subject": get_element_info_values(details_element, "field--name-field-materia"),
        "translator": get_element_info_values(details_element, "field--name-field-traduccion"),
        "imprint": get_element_info_values(details_element, "field--name-field-resp")
    }

    # Añadir campos
    for k, v in fields.items():
        if v is not None:
            data[k] = v

    # Metadata que requiere procesamiento
    
    # Derechos (licencia)
    derechos = get_element_info_values(details_element, "field--name-field-derechos")
    if derechos:
        # Añadir como nota descriptiva
        data["description"] = (
            data.get("description", "")
            + "\n\nDerechos: "
            + derechos
        )
            
    # Área
    area = details_element.find("div", class_="field--name-field-area").text
    if area:
        if "subject" in data:
            if isinstance(data["subject"], list):
                data["subject"].insert(0, area)
                print(data["subject"])
            else:
                data["subject"] = [area, data["subject"]]
        else:
            data["subject"] = area

    # Identificador
    isbn = get_element_info_values(details_element, "field--name-field-isbn")
    issn = get_element_info_values(details_element, "field--name-field-issn")
    if isbn:
        data["identifier"] = f"urn:ISBN:{isbn}"
    elif issn:
        data["identifier"] = f"urn:ISSN:{issn}"

    number_of_pages = get_element_info_values(details_element, "field--name-field-pages")
    if number_of_pages:
        data["numberOfPages"] = int(number_of_pages.replace("páginas", ""))

    # Contributor (illustrator/designer)
    illustrator = get_element_info_values(details_element, "field--name-field-diseno")
    if illustrator:
        data["illustrator"] = illustrator.strip(" ").split("/")

    # Colección
    coleccion = get_element_info_values(details_element, "field--name-field-coleccion")
    if coleccion:
        data["belongsTo"] = {"collection": coleccion}
    
    # Idioma por defecto
    data["language"] = "es"
    
    return data


def transform_to_opds(books, base_url="https://idartesencasa.gov.co"):
    """Transforma los datos al formato OPDS"""
    publications = []
    
    for book in books:
        # Agregar campos requeridos por OPDS
        metadata = {
            "@type": "http://schema.org/Book",
            "modified": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        # Combinar metadata con los datos del libro
        metadata.update({k: v for k, v in book.items() if k not in ["links", "images"]})

        publication = {
            "metadata": metadata,
            "links": book.get("links", []),
            "images": book.get("images", [])
        }
        
        publications.append(publication)
    
    # Estructura OPDS completa
    opds_feed = {
        "metadata": {
            "title": "Catálogo idartes",
            "numberOfItems": len(publications)
        },
        "links": [
            {
                "rel": "self",
                "href": f"{base_url}/libros_idartes.json",
                "type": "application/opds+json"
            }
        ],
        "publications": publications
    }
    
    return opds_feed


def save_opds_feed(opds_feed, filename="libros_idartes.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(opds_feed, f, ensure_ascii=False, indent=2)
    
    print(f"\nArchivo OPDS generado: {filename} ({opds_feed['metadata']['numberOfItems']} publicaciones)")


if __name__ == "__main__":
    path = "https://idartesencasa.gov.co"
    soup = get_soup(f'{path}/libros')
    books_url = get_books_url(soup)
    books = []
    
    for i, book_url in enumerate(books_url):
        print(f"{i+1}. {book_url.split('/')[-1]}")
        book_soup = get_soup(f'{path}{book_url}') 
        books.append(get_book_data(path, book_soup))
    
    # Transformar a formato OPDS y guardar
    opds_feed = transform_to_opds(books, path)
    save_opds_feed(opds_feed)
