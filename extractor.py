"""
Motor de extração de dados de XML de NF-e.

Extrai, da tag <dest>: Nome, CPF/CNPJ e UF (estado, de <enderDest>).
Extrai, de cada <det><prod>: Código e Descrição do produto.

Como uma NF-e pode ter vários produtos, cada arquivo XML pode gerar
VÁRIAS linhas de resultado (uma por produto), repetindo os dados do
destinatário em cada linha — isso facilita filtrar por Estado e por
Produto depois, na planilha.

Este módulo é usado tanto pela versão web (Streamlit) quanto pela
versão desktop, para não haver duas lógicas de extração divergentes.
"""

import xml.etree.ElementTree as ET


def _local_name(tag):
    """Remove o namespace da tag, ex: '{http://...}dest' -> 'dest'."""
    return tag.split('}')[-1] if '}' in tag else tag


def _find_first(elem, wanted_name):
    """Busca recursiva (case-insensitive) pelo primeiro elemento com esse nome local."""
    wanted_name = wanted_name.lower()
    for el in elem.iter():
        if _local_name(el.tag).lower() == wanted_name:
            return el
    return None


def _text(elem, wanted_name, default=''):
    found = _find_first(elem, wanted_name) if elem is not None else None
    if found is not None and found.text:
        return found.text.strip()
    return default


def extrair_dados_nfe(xml_source, nome_arquivo):
    """
    Extrai os dados de um XML de NF-e.

    xml_source: caminho do arquivo, objeto file-like, ou bytes.
    nome_arquivo: nome a ser exibido na coluna 'Arquivo'.

    Retorna uma lista de dicts (uma linha por produto encontrado).
    Se não houver produtos, retorna uma única linha com os campos de
    produto vazios. Em caso de erro de parsing, retorna uma única
    linha com a mensagem de erro na coluna 'Nome'.
    """
    try:
        tree = ET.parse(xml_source)
        root = tree.getroot()

        dest_elem = _find_first(root, 'dest')

        nome_valor = _text(dest_elem, 'xNome') if dest_elem is not None else ''
        cnpj_valor = _text(dest_elem, 'cnpj') if dest_elem is not None else ''
        cpf_valor = _text(dest_elem, 'cpf') if dest_elem is not None else ''

        ender_dest = _find_first(dest_elem, 'enderDest') if dest_elem is not None else None
        uf_valor = _text(ender_dest, 'uf') if ender_dest is not None else ''
        # fallback: às vezes a UF está direto em <dest>, sem <enderDest>
        if not uf_valor and dest_elem is not None:
            uf_valor = _text(dest_elem, 'uf')

        linha_base = {
            'Arquivo': nome_arquivo,
            'Nome': nome_valor,
            'CPF': cpf_valor,
            'CNPJ': cnpj_valor,
            'UF': uf_valor,
        }

        det_elems = [el for el in root.iter() if _local_name(el.tag).lower() == 'det']

        if not det_elems:
            linha_base['Codigo_Produto'] = ''
            linha_base['Descricao_Produto'] = ''
            return [linha_base]

        linhas = []
        for det in det_elems:
            prod = _find_first(det, 'prod')
            cprod = _text(prod, 'cProd') if prod is not None else ''
            xprod = _text(prod, 'xProd') if prod is not None else ''
            linha = dict(linha_base)
            linha['Codigo_Produto'] = cprod
            linha['Descricao_Produto'] = xprod
            linhas.append(linha)

        return linhas

    except Exception as e:
        return [{
            'Arquivo': nome_arquivo,
            'Nome': f'Erro: {e}',
            'CPF': '',
            'CNPJ': '',
            'UF': '',
            'Codigo_Produto': '',
            'Descricao_Produto': '',
        }]


COLUNAS = ['Arquivo', 'Nome', 'CPF', 'CNPJ', 'UF', 'Codigo_Produto', 'Descricao_Produto']
