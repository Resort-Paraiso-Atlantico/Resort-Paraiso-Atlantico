import unicodedata
import re

def normalizar_texto(texto: str) -> str:
    """
    Remove acentos, caracteres especiais e converte para minúsculas.
    Exemplo: 'Água Mineral' -> 'agua mineral'
    """
    if not texto:
        return ""
    # NFD decompõe caracteres acentuados (ex: 'á' -> 'a' + '´')
    nfkd = unicodedata.normalize("NFD", str(texto))
    texto_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return texto_sem_acento.lower().strip()

def sanitizar_documento(documento: str) -> str:
    """
    Remove todos os caracteres não numéricos de um CPF ou CNPJ.
    Exemplo: '123.456.789-00' -> '12345678900'
    """
    if not documento:
        return ""
    return re.sub(r"\D", "", str(documento))

def atende_termo_busca(termo: str, *valores: str) -> bool:
    """
    Verifica se o termo de busca (normalizado) está contido em qualquer um dos valores fornecidos.
    """
    if not termo:
        return True
    termo_norm = normalizar_texto(termo)
    for val in valores:
        if val and termo_norm in normalizar_texto(str(val)):
            return True
    return False
