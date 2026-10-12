from datetime import datetime
import xml.etree.ElementTree as ET
import hashlib
from services.base import db_session, db_connection

def get_config(chave, default=""):
    with db_connection() as conn:
        r = conn.execute("SELECT valor FROM config_fiscal WHERE chave=?", (chave,)).fetchone()
        return r[0] if r else default

def set_config(chave, valor):
    with db_session() as conn:
        conn.execute("INSERT OR REPLACE INTO config_fiscal (chave, valor) VALUES (?, ?)", (chave, valor))

def listar_config():
    with db_connection() as conn:
        r = conn.execute("SELECT chave, valor FROM config_fiscal ORDER BY chave").fetchall()
        return {row["chave"]: row["valor"] for row in r}

def gerar_xml_e_fatura(doc_id):
    with db_session() as conn:
        doc = conn.execute("SELECT * FROM documentos_fiscais WHERE id=?", (doc_id,)).fetchone()
        if not doc:
            return None
        empresa_nif = get_config("empresa_nif", "000000000")
        empresa_nome = get_config("empresa_nome", "Minha Empresa")
        chave_validacao = get_config("at_validacao_key", "AT-MZ-DEV-KEY")

        root = ET.Element("eFactura")
        root.set("xmlns", "http://www.at.gov.mz/eFactura")
        root.set("versao", "1.0")

        cab = ET.SubElement(root, "Cabecalho")
        ET.SubElement(cab, "TipoDocumento").text = doc["tipo_documento"]
        ET.SubElement(cab, "Serie").text = doc["serie"]
        ET.SubElement(cab, "NumeroDocumento").text = str(doc["numero"])
        ET.SubElement(cab, "DataEmissao").text = doc["data_emissao"]
        ET.SubElement(cab, "Hash").text = doc["hash"]
        ET.SubElement(cab, "NIFEmitente").text = empresa_nif
        ET.SubElement(cab, "NomeEmitente").text = empresa_nome

        emi = ET.SubElement(root, "Emitente")
        ET.SubElement(emi, "NIF").text = empresa_nif
        ET.SubElement(emi, "Nome").text = empresa_nome
        ET.SubElement(emi, "Endereco").text = get_config("empresa_endereco", "")
        ET.SubElement(emi, "Telefone").text = get_config("empresa_telefone", "")

        adq = ET.SubElement(root, "Adquirente")
        ET.SubElement(adq, "NIF").text = doc["cliente_nif"] or "999999999"
        ET.SubElement(adq, "Nome").text = doc["cliente_nome"] or "Consumidor Final"

        det = ET.SubElement(root, "Detalhe")
        ET.SubElement(det, "Total").text = f"{doc['total']:.2f}"
        ET.SubElement(det, "TotalIVA").text = f"{doc['iva_total']:.2f}"

        qr_raw = f"{doc['tipo_documento']}|{doc['serie']}|{doc['numero']}|{doc['data_emissao']}|{doc['total']}|{chave_validacao}"
        qr_hash = hashlib.sha256(qr_raw.encode()).hexdigest().upper()
        ET.SubElement(root, "QRCode").text = qr_hash

        xml_str = ET.tostring(root, encoding="unicode", xml_declaration=True)
        conn.execute("UPDATE documentos_fiscais SET at_xml=?, qrcode=? WHERE id=?",
                   (xml_str, qr_hash, doc_id))
        return xml_str

def listar_documentos_at(status=None, filial_id=1, limite=100):
    with db_connection() as conn:
        sql = "SELECT * FROM documentos_fiscais WHERE filial_id=?"
        params = [filial_id]
        if status:
            sql += " AND at_status=?"
            params.append(status)
        sql += " ORDER BY data_emissao DESC LIMIT ?"
        params.append(limite)
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def simular_enviar_at(doc_id):
    with db_session() as conn:
        doc = conn.execute("SELECT * FROM documentos_fiscais WHERE id=?", (doc_id,)).fetchone()
        if not doc:
            return {"ok": False, "erro": "Documento não encontrado"}

        xml = doc["at_xml"]
        if not xml:
            xml = gerar_xml_e_fatura(doc_id)
            if not xml:
                return {"ok": False, "erro": "Erro ao gerar XML"}

        tentativas = (doc["at_tentativas"] or 0) + 1
        ambiente = get_config("at_ambiente", "teste")

        if doc["total"] and doc["cliente_nif"]:
            sucesso = True
            resposta = f"Documento validado com sucesso (ambiente: {ambiente})"
            novo_status = "validado"
        else:
            sucesso = False
            resposta = "Documento rejeitado: dados insuficientes"
            novo_status = "rejeitado"

        conn.execute("UPDATE documentos_fiscais SET at_status=?, at_mensagem=?, at_data_envio=datetime('now','localtime'), at_tentativas=? WHERE id=?",
                   (novo_status, resposta, tentativas, doc_id))
        conn.execute("INSERT INTO fiscal_at_log (documento_fiscal_id, tipo, status, xml_enviado, resposta) VALUES (?,?,?,?,?)",
                   (doc_id, "envio", novo_status, xml, resposta))
        return {"ok": sucesso, "status": novo_status, "resposta": resposta}

def enviar_pendentes(filial_id=1):
    with db_connection() as conn:
        pendentes = conn.execute("SELECT id FROM documentos_fiscais WHERE at_status IS NULL AND filial_id=? LIMIT 50", (filial_id,)).fetchall()
    resultados = []
    for p in pendentes:
        res = simular_enviar_at(p["id"])
        resultados.append({"id": p["id"], **res})
    return resultados

def gerar_saft(pt="MZ", filial_id=1):
    with db_connection() as conn:
        docs = conn.execute("SELECT * FROM documentos_fiscais WHERE filial_id=? AND status='normal' ORDER BY data_emissao DESC LIMIT 1000", (filial_id,)).fetchall()
    empresa_nif = get_config("empresa_nif", "000000000")
    empresa_nome = get_config("empresa_nome", "Minha Empresa")

    root = ET.Element("AuditFile")
    root.set("xmlns", "http://www.at.gov.mz/SAFT")
    root.set("versao", "1.0")

    header = ET.SubElement(root, "Header")
    ET.SubElement(header, "CompanyName").text = empresa_nome
    ET.SubElement(header, "CompanyTaxID").text = empresa_nif
    ET.SubElement(header, "TaxAccountingBasis").text = "Accrual"
    ET.SubElement(header, "Currency").text = "MZN"
    ET.SubElement(header, "DateCreated").text = datetime.now().strftime("%Y-%m-%d")

    docs_elem = ET.SubElement(root, "Documents")
    for doc in docs:
        d = ET.SubElement(docs_elem, "Document")
        ET.SubElement(d, "Type").text = doc["tipo_documento"]
        ET.SubElement(d, "Series").text = doc["serie"]
        ET.SubElement(d, "Number").text = str(doc["numero"])
        ET.SubElement(d, "Date").text = doc["data_emissao"]
        ET.SubElement(d, "CustomerName").text = doc["cliente_nome"] or "Consumidor Final"
        ET.SubElement(d, "CustomerTaxID").text = doc["cliente_nif"] or "999999999"
        ET.SubElement(d, "Total").text = f"{doc['total']:.2f}"
        ET.SubElement(d, "IVA").text = f"{doc['iva_total']:.2f}"

    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=True)
    return xml_str

def obter_log_envio(documento_fiscal_id):
    with db_connection() as conn:
        r = conn.execute("SELECT * FROM fiscal_at_log WHERE documento_fiscal_id=? ORDER BY data_envio DESC",
                       (documento_fiscal_id,)).fetchall()
        return [dict(row) for row in r]
