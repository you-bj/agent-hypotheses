"""
Module de chargement et découpage de documents PDF
pour l'indexation dans le RAG.
"""

from pypdf import PdfReader


def load_pdf(pdf_path: str) -> list[dict]:
    """
    Charge un fichier PDF et extrait le texte de chaque page.

    Les pages contenant moins de 50 caractères sont ignorées
    (pages blanches, pages de garde, etc.).

    Args:
        pdf_path: Chemin vers le fichier PDF à charger.

    Returns:
        list[dict]: Liste de dictionnaires avec les clés :
            - page (int) : numéro de la page (1-indexé)
            - text (str) : texte extrait de la page
    """
    reader = PdfReader(pdf_path)
    pages = []

    for i, page in enumerate(reader.pages):
        texte = page.extract_text() or ""
        texte = texte.strip()

        # Ignorer les pages avec moins de 50 caractères
        if len(texte) < 50:
            continue

        pages.append({
            "page": i + 1,
            "text": texte,
        })

    return pages


def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Découpe les pages en morceaux (chunks) de taille fixe avec chevauchement.

    Args:
        pages: Liste de dictionnaires retournée par load_pdf().
        chunk_size: Taille maximale de chaque chunk en caractères.
        overlap: Nombre de caractères de chevauchement entre chunks consécutifs.

    Returns:
        list[dict]: Liste de dictionnaires avec les clés :
            - chunk_id (str) : identifiant unique du chunk (ex: "page3_chunk2")
            - text (str) : texte du chunk
            - page (int) : numéro de la page source
    """
    chunks = []
    chunk_counter = 0

    for page_data in pages:
        texte = page_data["text"]
        num_page = page_data["page"]
        start = 0

        while start < len(texte):
            end = start + chunk_size
            chunk_text_content = texte[start:end]

            chunk_counter += 1
            chunks.append({
                "chunk_id": f"page{num_page}_chunk{chunk_counter}",
                "text": chunk_text_content,
                "page": num_page,
            })

            # Avancer avec le chevauchement
            start += chunk_size - overlap

    return chunks
