import struct, zlib, datetime, os

class PDFReport:
    def __init__(self, title="Relatório", page_width=595, page_height=842):
        self.page_w = page_width
        self.page_h = page_height
        self.ml, self.mr = 40, 40
        self.mt, self.mb = 40, 50
        self.body_w = page_width - self.ml - self.mr
        self.title = title
        self.objects = []
        self.obj_count = 0
        self.pages = []
        self.current_page = []
        self.fonts = {}
        self.y = page_height - self.mt

    def _new_id(self):
        self.obj_count += 1
        return self.obj_count

    def _add_obj(self, content):
        oid = self._new_id()
        self.objects.append((oid, content))
        return oid

    def _escape(self, s):
        s = s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        s = s.encode('cp1252', 'replace').decode('cp1252')
        return s

    def _rgb(self, r, g, b):
        return f'{r/255:.3f} {g/255:.3f} {b/255:.3f} rg'

    def _stream_cmd(self, cmd):
        self.current_page.append(cmd.encode('cp1252'))

    def new_page(self):
        if self.current_page:
            self.pages.append(b'\n'.join(self.current_page))
        self.current_page = []
        self.y = self.page_h - self.mt

    def _check_page(self, needed=30):
        if self.y - needed < self.mb:
            self.new_page()

    def add_title(self, text, size=18, bold=True):
        self._check_page(40)
        font = '/F1' if bold else '/F2'
        self._stream_cmd(f'BT {font} {size} Tf {self._rgb(30,30,30)} 1 0 0 1 {self.ml} {self.y} Tm ({self._escape(text)}) Tj ET')
        self.y -= size + 8

    def add_subtitle(self, text, size=10):
        self._check_page(20)
        self._stream_cmd(f'BT /F2 {size} Tf {self._rgb(100,100,100)} 1 0 0 1 {self.ml} {self.y} Tm ({self._escape(text)}) Tj ET')
        self.y -= size + 4

    def add_line(self):
        self._check_page(10)
        y_line = self.y
        self._stream_cmd(f'1 w 0 0 0 RG {self.ml} {y_line} m {self.ml+self.body_w} {y_line} l S')
        self.y -= 10

    def add_text(self, text, size=10, indent=0):
        self._check_page(size + 4)
        self._stream_cmd(f'BT /F2 {size} Tf {self._rgb(50,50,50)} 1 0 0 1 {self.ml+indent} {self.y} Tm ({self._escape(text)}) Tj ET')
        self.y -= size + 4

    def add_table(self, headers, rows, col_widths=None, header_size=9, row_size=8):
        if not col_widths:
            n = len(headers)
            col_widths = [self.body_w // n] * n
            remaining = self.body_w - sum(col_widths)
            col_widths[-1] += remaining
        row_h = 16
        header_h = 20
        total_h = header_h + len(rows) * row_h + 6
        self._check_page(total_h + 10)
        x_positions = [self.ml]
        for w in col_widths:
            x_positions.append(x_positions[-1] + w)
        y_table = self.y
        self._stream_cmd(f'{self._rgb(59,130,246)} 0 0 0 rg')
        self._stream_cmd(f'{self.ml} {y_table - header_h} {self.body_w} {header_h} re f')
        self._stream_cmd(f'1 w 0 0 0 RG')
        for i, h in enumerate(headers):
            cx = x_positions[i] + col_widths[i] / 2
            self._stream_cmd(f'BT /F1 {header_size} Tf 1 0 0 1 {cx} {y_table - 14} Tm 0.5 -0.5 Td ({self._escape(h)}) Tj ET')
        self._stream_cmd(f'{self.ml} {y_table - header_h} m {self.ml+self.body_w} {y_table - header_h} l S')
        y_row = y_table - header_h
        for ri, row in enumerate(rows):
            y_row -= row_h
            if ri % 2 == 1:
                self._stream_cmd(f'{self._rgb(245,247,250)} {self.ml} {y_row} {self.body_w} {row_h} re f')
            for ci, val in enumerate(row):
                cx = x_positions[ci] + 4
                self._stream_cmd(f'BT /F2 {row_size} Tf {self._rgb(50,50,50)} 1 0 0 1 {cx} {y_row + 4} Tm ({self._escape(str(val))}) Tj ET')
        self.y = y_row - 4

    def add_footer(self, page_num, total_pages):
        self._stream_cmd(f'BT /F2 7 Tf {self._rgb(150,150,150)} 1 0 0 1 {self.ml} {20} Tm (Página {page_num} de {total_pages}) Tj ET')

    def build(self):
        self.new_page()
        pages_content = []
        for pi, page_data in enumerate(self.pages):
            compressed = zlib.compress(page_data)
            font_f1 = self._add_obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
            font_f2 = self._add_obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>')
            proc_set = self._add_obj('<< /ProcSet [/PDF /Text] >>')
            resources = f'<< /Font << /F1 {font_f1} 0 R /F2 {font_f2} 0 R >> /ProcSet {proc_set} 0 R >>'
            content_obj = self._add_obj(f'<< /Length {len(compressed)} /Filter /FlateDecode >>\nstream\n{compressed.decode("latin-1")}\nendstream')
            page_obj = self._add_obj(f'<< /Type /Page /Parent {len(pages_content)+1} 0 R /MediaBox [0 0 {self.page_w} {self.page_h}] /Contents {content_obj} 0 R /Resources {resources} >>')
            pages_content.append(page_obj)
        pages_root = self._add_obj(f'<< /Type /Pages /Kids [{" ".join(f"{p} 0 R" for p in pages_content)}] /Count {len(pages_content)} >>')
        catalog = self._add_obj('<< /Type /Catalog /Pages ' + f'{pages_root} 0 R >>')
        xref_offset = None
        lines = ['%PDF-1.4']
        offsets = []
        for oid, content in self.objects:
            offsets.append(sum(len(l)+1 for l in lines))
            lines.append(f'{oid} 0 obj\n{content}\nendobj')
        xref_offset = sum(len(l)+1 for l in lines)
        lines.append('xref')
        lines.append(f'0 {self.obj_count+1}')
        lines.append('0000000000 65535 f ')
        for offset in offsets:
            lines.append(f'{offset:010d} 00000 n ')
        lines.append('trailer')
        lines.append(f'<< /Size {self.obj_count+1} /Root {catalog} 0 R >>')
        lines.append('startxref')
        lines.append(str(xref_offset))
        lines.append('%%EOF')
        return '\n'.join(lines).encode('latin-1')


def gerar_pdf_relatorio(titulo, periodo, headers, rows, col_widths=None, filename=None):
    pdf = PDFReport(titulo)
    pdf.add_title(titulo, 20)
    pdf.add_subtitle(periodo, 10)
    pdf.add_line()
    pdf.add_text(f'Gerado em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', 8)
    pdf.add_text(f'Total de registos: {len(rows)}', 8)
    pdf.add_line()
    pdf.add_table(headers, rows, col_widths)
    data = pdf.build()
    if filename:
        with open(filename, 'wb') as f:
            f.write(data)
        return filename
    return data
