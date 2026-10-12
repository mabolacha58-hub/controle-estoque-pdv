from services.base import db_session, db_connection
import hashlib, json, os

TIPOS_DOCUMENTO = {
    "FT": "Factura",
    "FR": "Factura-Recibo",
    "GR": "Guia de Remessa",
    "NC": "Nota de Crédito",
    "ND": "Nota de Débito",
}

def obter_proximo_numero(tipo_documento, filial_id=1):
    with db_session() as conn:
        serie = conn.execute('''SELECT id, serie, numero_atual FROM series_fiscais
                              WHERE tipo_documento=? AND filial_id=? AND ativo=1
                              ORDER BY id LIMIT 1''', (tipo_documento, filial_id)).fetchone()
        if not serie:
            return None, None
        prox_num = serie["numero_atual"] + 1
        conn.execute("UPDATE series_fiscais SET numero_atual=? WHERE id=?", (prox_num, serie["id"]))
        return serie["serie"], prox_num

def gerar_hash(serie, numero, data, total, chave_empresa=None):
    if chave_empresa is None:
        chave_empresa = os.environ.get('FISCAL_HASH_KEY', 'CHAVE_PADRAO')
    raw = f"{serie}|{numero}|{data}|{total}|{chave_empresa}"
    return hashlib.sha256(raw.encode()).hexdigest().upper()

def emitir_documento(tipo_documento, cliente_id, cliente_nome, cliente_nif, total, iva_total, venda_id=None, filial_id=1):
    serie, numero = obter_proximo_numero(tipo_documento, filial_id)
    if not serie:
        return None
    hash_val = gerar_hash(serie, numero, None, total)
    with db_session() as conn:
        c = conn.execute('''INSERT INTO documentos_fiscais
                          (tipo_documento,serie,numero,hash,cliente_id,cliente_nome,cliente_nif,total,iva_total,venda_id,filial_id)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                       (tipo_documento, serie, numero, hash_val, cliente_id, cliente_nome, cliente_nif,
                        total, iva_total, venda_id, filial_id))
        return {"id": c.lastrowid, "tipo": tipo_documento, "serie": serie, "numero": numero, "hash": hash_val}

def listar_documentos(tipo_documento=None, filial_id=1, limite=50):
    with db_connection() as conn:
        sql = "SELECT * FROM documentos_fiscais WHERE filial_id=?"
        params = [filial_id]
        if tipo_documento:
            sql += " AND tipo_documento=?"
            params.append(tipo_documento)
        sql += " ORDER BY data_emissao DESC LIMIT ?"
        params.append(limite)
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def anular_documento(id, motivo=""):
    with db_session() as conn:
        doc = conn.execute("SELECT * FROM documentos_fiscais WHERE id=?", (id,)).fetchone()
        if not doc or doc["status"] == "anulado":
            return False
        conn.execute('''UPDATE documentos_fiscais SET status='anulado', data_anulacao=datetime('now','localtime')
                      WHERE id=?''', (id,))
        return True

def listar_series(tipo_documento=None, filial_id=1):
    with db_connection() as conn:
        if tipo_documento:
            r = conn.execute("SELECT * FROM series_fiscais WHERE tipo_documento=? AND filial_id=? ORDER BY serie",
                           (tipo_documento, filial_id)).fetchall()
        else:
            r = conn.execute("SELECT * FROM series_fiscais WHERE filial_id=? ORDER BY tipo_documento, serie",
                           (filial_id,)).fetchall()
        return [dict(row) for row in r]
