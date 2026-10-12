import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import os
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), 'controle_estoque.db')

# Cores
COR_BG = "#0d1117"
COR_BG2 = "#161b22"
COR_BG3 = "#21262d"
COR_BORDA = "#30363d"
COR_TEXTO = "#e6edf3"
COR_TEXTO2 = "#8b949e"
COR_PRIMARIA = "#7c3aed"
COR_SUCESSO = "#22c55e"
COR_PERIGO = "#ef4444"
COR_AVISO = "#eab308"
COR_INFO = "#3b82f6"
COR_ROSA = "#ec4899"

import unicodedata

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, descricao TEXT
        );
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, codigo_barras TEXT,
            descricao TEXT, categoria_id INTEGER, quantidade REAL DEFAULT 0,
            quantidade_minima REAL DEFAULT 0, preco_custo REAL DEFAULT 0,
            preco_venda REAL DEFAULT 0, unidade TEXT DEFAULT 'UN',
            data_criacao TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, quantidade REAL NOT NULL, preco_unitario REAL DEFAULT 0,
            data TEXT DEFAULT (datetime('now','localtime')), documento TEXT, observacao TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    ''')
    categorias_padrao = [
        ("Alimentos", "Produtos alimentícios em geral"),
        ("Bebidas", "Bebidas e líquidos"),
        ("Limpeza", "Produtos de limpeza e higiene"),
        ("Ferramentas", "Ferramentas e utensílios"),
        ("Material de Escritório", "Papelaria e materiais de escritório"),
        ("Vestuário", "Roupas e uniformes"),
        ("Eletrônicos", "Equipamentos eletrônicos"),
        ("Embalagens", "Caixas, sacos e materiais de embalagem"),
        ("Matéria-Prima", "Insumos para produção"),
        ("Outros", "Produtos diversos"),
    ]
    for nome, desc in categorias_padrao:
        try:
            c.execute("INSERT INTO categorias (nome, descricao) VALUES (?, ?)", (nome, desc))
        except:
            pass
    conn.commit()
    conn.close()

def exportar_csv(dados, cabecalhos, nome_padrao="exportacao"):
    path = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV", "*.csv")],
        initialfile=f"{nome_padrao}_{datetime.now().strftime('%Y%m%d')}.csv")
    if not path: return
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(cabecalhos)
        w.writerows(dados)
    messagebox.showinfo("Exportado", f"Dados salvos em:\n{path}")

def configurar_estilo():
    estilo = ttk.Style()
    estilo.theme_use("clam")

    estilo.configure(".", bg=COR_BG, fg=COR_TEXTO, fieldbackground=COR_BG2,
                     troughcolor=COR_BG2, selectbackground=COR_PRIMARIA, selectforeground="white",
                     font=("Segoe UI", 10))

    estilo.configure("TNotebook", bg=COR_BG, borderwidth=0)
    estilo.configure("TNotebook.Tab", bg=COR_BG2, fg=COR_TEXTO2, padding=[22, 9],
                     borderwidth=0, focuscolor="none")
    estilo.map("TNotebook.Tab", background=[("selected", COR_PRIMARIA)],
               foreground=[("selected", "white")])

    estilo.configure("Treeview", bg=COR_BG2, fg=COR_TEXTO, fieldbackground=COR_BG2,
                     borderwidth=0, rowheight=34)
    estilo.map("Treeview", background=[("selected", COR_PRIMARIA)], foreground=[("selected", "white")])
    estilo.configure("Treeview.Heading", bg=COR_BG3, fg=COR_TEXTO, borderwidth=0,
                     relief="flat", font=("Segoe UI", 9, "bold"))
    estilo.map("Treeview.Heading", background=[("active", COR_BG3)])

    estilo.configure("TButton", bg=COR_PRIMARIA, fg="white", borderwidth=0,
                     focuscolor="none", padding=[15, 8], font=("Segoe UI", 10, "bold"))
    estilo.map("TButton", background=[("active", "#8b5cf6"), ("pressed", "#6d28d9")])

    estilo.configure("Success.TButton", bg=COR_SUCESSO, fg="white")
    estilo.map("Success.TButton", background=[("active", "#16a34a"), ("pressed", "#15803d")])

    estilo.configure("Danger.TButton", bg=COR_PERIGO, fg="white")
    estilo.map("Danger.TButton", background=[("active", "#dc2626"), ("pressed", "#b91c1c")])

    estilo.configure("Outline.TButton", bg=COR_BG3, fg=COR_TEXTO, borderwidth=1,
                     bordercolor=COR_BORDA, font=("Segoe UI", 10))
    estilo.map("Outline.TButton", background=[("active", COR_BORDA)])

    estilo.configure("TLabel", bg=COR_BG, fg=COR_TEXTO)
    estilo.configure("TFrame", bg=COR_BG)
    estilo.configure("TLabelframe", bg=COR_BG, fg=COR_TEXTO, borderwidth=1, bordercolor=COR_BORDA)
    estilo.configure("TLabelframe.Label", bg=COR_BG, fg=COR_TEXTO)

    estilo.configure("TEntry", fieldbackground=COR_BG2, fg=COR_TEXTO, borderwidth=1,
                     bordercolor=COR_BORDA, padding=[8, 4])
    estilo.map("TEntry", bordercolor=[("focus", COR_PRIMARIA)])

    estilo.configure("TCombobox", fieldbackground=COR_BG2, fg=COR_TEXTO, borderwidth=1,
                     bordercolor=COR_BORDA, arrowcolor=COR_TEXTO, padding=[8, 4])
    estilo.map("TCombobox", bordercolor=[("focus", COR_PRIMARIA)])

    estilo.configure("Search.TEntry", fieldbackground=COR_BG3, fg=COR_TEXTO2, borderwidth=1,
                     bordercolor=COR_BORDA, padding=[10, 6])

class CardWidget(tk.Frame):
    def __init__(self, parent, titulo, valor, icone, cor=COR_PRIMARIA, largura=210):
        super().__init__(parent, bg=COR_BG2, highlightbackground=COR_BORDA,
                         highlightthickness=1, width=largura, height=105)
        self.pack_propagate(False)

        self.accent = tk.Frame(self, bg=cor, height=3)
        self.accent.pack(fill='x')

        inner = tk.Frame(self, bg=COR_BG2, padx=14, pady=10)
        inner.pack(fill='both', expand=True)

        top = tk.Frame(inner, bg=COR_BG2)
        top.pack(fill='x')

        self.lbl_icone = tk.Label(top, text=icone, font=("Segoe UI", 18), bg=COR_BG2, fg=cor)
        self.lbl_icone.pack(side='left')

        self.lbl_valor = tk.Label(top, text=str(valor), font=("Segoe UI", 26, "bold"),
                                  bg=COR_BG2, fg="white")
        self.lbl_valor.pack(side='right')

        self.lbl_titulo = tk.Label(inner, text=titulo, font=("Segoe UI", 9),
                                   bg=COR_BG2, fg=COR_TEXTO2, anchor='w')
        self.lbl_titulo.pack(fill='x')
        self.cor = cor

    def atualizar(self, valor, cor=None):
        self.lbl_valor.config(text=str(valor))
        if cor:
            self.cor = cor
            self.lbl_valor.config(fg=cor)
            self.lbl_icone.config(fg=cor)
            self.accent.config(bg=cor)

class ControleEstoqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Estoque")
        self.root.geometry("1250x750")
        self.root.configure(bg=COR_BG)

        configurar_estilo()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=12, pady=(0, 8))

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_pdv = ttk.Frame(self.notebook)
        self.tab_produtos = ttk.Frame(self.notebook)
        self.tab_movimentacoes = ttk.Frame(self.notebook)
        self.tab_categorias = ttk.Frame(self.notebook)
        self.tab_relatorios = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="\U0001f4ca  Dashboard")
        self.notebook.add(self.tab_pdv, text="\U0001f7e1  PDV")
        self.notebook.add(self.tab_produtos, text="\U0001f4e6  Produtos")
        self.notebook.add(self.tab_movimentacoes, text="\U0001f504  Movimentações")
        self.notebook.add(self.tab_categorias, text="\U0001f4c2  Categorias")
        self.notebook.add(self.tab_relatorios, text="\U0001f4cb  Relatórios")

        self.build_dashboard()
        self.build_pdv()
        self.build_produtos()
        self.build_movimentacoes()
        self.build_categorias()
        self.build_relatorios()

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._bind_notebook_keys()
        self._init_nav_campos()
        self.root.after(100, lambda: self.pdv_search.focus())

        self.status_bar = tk.Frame(root, bg=COR_BG3, height=28)
        self.status_bar.pack(fill='x')
        self.status_label = tk.Label(self.status_bar, text="Pronto", font=("Segoe UI", 9),
                                      bg=COR_BG3, fg=COR_TEXTO2, padx=12)
        self.status_label.pack(side='left')
        self.db_label = tk.Label(self.status_bar, text=f"DB: controle_estoque.db",
                                  font=("Segoe UI", 9), bg=COR_BG3, fg=COR_TEXTO2, padx=12)
        self.db_label.pack(side='right')

    def _bind_notebook_keys(self):
        self.root.bind('<Control-Tab>', lambda e: self._trocar_aba(1))
        self.root.bind('<Control-ISO_Left_Tab>', lambda e: self._trocar_aba(-1))
        self.root.bind('<Control-Shift-Tab>', lambda e: self._trocar_aba(-1))
        self.root.bind('<Control-Left>', lambda e: self._trocar_aba(-1))
        self.root.bind('<Control-Right>', lambda e: self._trocar_aba(1))
        self.root.bind('<Control-Up>', lambda e: self._trocar_aba(-1))
        self.root.bind('<Control-Down>', lambda e: self._trocar_aba(1))
        self.root.bind('<Alt-Left>', lambda e: self._trocar_aba(-1))
        self.root.bind('<Alt-Right>', lambda e: self._trocar_aba(1))

    def _trocar_aba(self, direcao):
        atual = self.notebook.index(self.notebook.select())
        total = self.notebook.index('end')
        nova = (atual + direcao) % total
        self.notebook.select(nova)

    def _focar_tree(self, tree):
        tree.focus_set()
        children = tree.get_children()
        if children:
            tree.selection_set(children[0])

    def _init_nav_campos(self):
        self.root.bind_class('nav_campo', '<Up>', self._navegar_campo)
        self.root.bind_class('nav_campo', '<Down>', self._navegar_campo)
        for w in self._coletar_campos():
            self._bind_campo_nav(w)
        self.root.bind('<FocusIn>', self._novo_foco, add='+')

    def _bind_campo_nav(self, w):
        tags = list(w.bindtags())
        clazz = w.winfo_class()
        if clazz in tags and 'nav_campo' not in tags:
            tags.insert(tags.index(clazz), 'nav_campo')
            w.bindtags(tuple(tags))

    def _novo_foco(self, event):
        w = event.widget
        if isinstance(w, (tk.Entry, ttk.Entry, ttk.Combobox, ttk.Spinbox)):
            if 'nav_campo' not in w.bindtags():
                self._bind_campo_nav(w)

    def _coletar_campos(self, parent=None):
        if parent is None:
            parent = self.root
        campos = []
        for child in parent.winfo_children():
            if isinstance(child, (tk.Entry, ttk.Entry, ttk.Combobox, ttk.Spinbox)):
                if child.winfo_ismapped() and child.winfo_viewable():
                    campos.append(child)
            elif isinstance(child, (tk.Frame, ttk.Frame, tk.LabelFrame, ttk.LabelFrame,
                                     ttk.Notebook, tk.PanedWindow)):
                campos.extend(self._coletar_campos(child))
        return campos

    def _navegar_campo(self, event):
        w = event.widget
        if not isinstance(w, (tk.Entry, ttk.Entry, ttk.Combobox, ttk.Spinbox)):
            return
        top = w.winfo_toplevel()
        campos = self._coletar_campos(top)
        if len(campos) < 2:
            return
        try:
            idx = campos.index(w)
        except ValueError:
            return
        prox = (idx + (1 if event.keysym == 'Down' else -1)) % len(campos)
        campos[prox].focus_set()
        return 'break'

    def _on_tab_changed(self, event=None):
        self.atualizar_tudo()
        tab_map = {
            self.tab_dashboard: None,
            self.tab_pdv: self.tree_pdv,
            self.tab_produtos: self.tree_prod,
            self.tab_movimentacoes: self.tree_mov,
            self.tab_categorias: self.tree_cat,
        }
        tree = tab_map.get(self.notebook.nametowidget(self.notebook.select()))
        if tree:
            self._focar_tree(tree)

    def query(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(sql, params)
        conn.commit()
        data = c.fetchall()
        conn.close()
        return data

    def refresh_tree(self, tree, cols, q, params=()):
        for row in tree.get_children():
            tree.delete(row)
        for row in self.query(q, params):
            tree.insert('', 'end', values=row)

    def atualizar_tudo(self):
        self.update_dashboard()
        self.update_pdv_produtos()
        self.update_produtos()
        self.update_movimentacoes()
        self.update_categorias()
        self.status_label.config(text=f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")

    # ===================== DASHBOARD =====================
    def build_dashboard(self):
        f = self.tab_dashboard

        # Cabeçalho com data
        cab = tk.Frame(f, bg=COR_BG)
        cab.pack(fill='x', pady=(12, 2))
        tk.Label(cab, text="Dashboard", font=("Segoe UI", 20, "bold"),
                 bg=COR_BG, fg="white").pack(side='left')
        tk.Label(cab, text=datetime.now().strftime("%d/%m/%Y"),
                 font=("Segoe UI", 10), bg=COR_BG, fg=COR_TEXTO2).pack(side='right')

        # Cards compactos
        c_frame = tk.Frame(f, bg=COR_BG)
        c_frame.pack(fill='x', pady=(8, 5))

        stats = [
            ("Produtos", 0, COR_PRIMARIA),
            ("Categorias", 0, COR_INFO),
            ("Movimentações", 0, COR_SUCESSO),
            ("Estoque Baixo", 0, COR_PERIGO),
            ("Valor Total", "MT 0", COR_AVISO),
        ]
        self.cards = {}
        for texto, val, cor in stats:
            fcard = tk.Frame(c_frame, bg=COR_BG2, highlightbackground=COR_BORDA,
                             highlightthickness=1, width=190, height=70)
            fcard.pack(side='left', padx=3)
            fcard.pack_propagate(False)
            tk.Frame(fcard, bg=cor, height=3).pack(fill='x')
            inner = tk.Frame(fcard, bg=COR_BG2, padx=10, pady=6)
            inner.pack(fill='both', expand=True)
            lbl_v = tk.Label(inner, text=str(val), font=("Segoe UI", 18, "bold"),
                             bg=COR_BG2, fg=cor)
            lbl_v.pack(anchor='w')
            tk.Label(inner, text=texto, font=("Segoe UI", 8),
                     bg=COR_BG2, fg=COR_TEXTO2).pack(anchor='w')
            self.cards[texto] = lbl_v

        # Grid principal
        grid = tk.Frame(f, bg=COR_BG)
        grid.pack(fill='both', expand=True, pady=2)

        # Esquerda (gráfico principal)
        esq = tk.Frame(grid, bg=COR_BG)
        esq.pack(side='left', fill='both', expand=True)

        # Gráfico de Linha GRANDE
        lf = tk.LabelFrame(esq, text="Movimentações (últimos 30 dias)", fg=COR_TEXTO,
                           bg=COR_BG, font=("Segoe UI", 10, "bold"), padx=6, pady=6)
        lf.pack(fill='both', expand=True, pady=(0, 3))
        self.line_canvas = tk.Canvas(lf, bg=COR_BG2, highlightthickness=0)
        self.line_canvas.pack(fill='both', expand=True)

        # Linha inferior: Donut + Barras
        inf = tk.Frame(esq, bg=COR_BG)
        inf.pack(fill='x')

        # Donut
        df = tk.LabelFrame(inf, text="Produtos por Categoria", fg=COR_TEXTO,
                           bg=COR_BG, font=("Segoe UI", 10, "bold"), padx=6, pady=6)
        df.pack(side='left', fill='both', expand=True, padx=(0, 2))
        self.donut_canvas = tk.Canvas(df, bg=COR_BG2, highlightthickness=0, height=170)
        self.donut_canvas.pack(fill='both', expand=True)

        # Barras
        bf = tk.LabelFrame(inf, text="Top Produtos", fg=COR_TEXTO,
                           bg=COR_BG, font=("Segoe UI", 10, "bold"), padx=6, pady=6)
        bf.pack(side='left', fill='both', expand=True, padx=(2, 0))
        self.bars_canvas = tk.Canvas(bf, bg=COR_BG2, highlightthickness=0, height=170)
        self.bars_canvas.pack(fill='both', expand=True)

        # Direita (painel)
        direita = tk.Frame(grid, bg=COR_BG, width=260)
        direita.pack(side='right', fill='y', padx=(5, 0))
        direita.pack_propagate(False)

        painel = tk.LabelFrame(direita, text="Resumo", fg=COR_TEXTO,
                               bg=COR_BG, font=("Segoe UI", 10, "bold"), padx=8, pady=8)
        painel.pack(fill='both', expand=True)
        self.painel_lista = tk.Frame(painel, bg=COR_BG2)
        self.painel_lista.pack(fill='both', expand=True)

        self.update_dashboard()

    def update_dashboard(self):
        cards_data = [
            ("Produtos", "SELECT COUNT(*) FROM produtos", COR_PRIMARIA),
            ("Categorias", "SELECT COUNT(*) FROM categorias", COR_INFO),
            ("Movimentações", "SELECT COUNT(*) FROM movimentacoes", COR_SUCESSO),
        ]
        for nome, sql, cor in cards_data:
            self.cards[nome].config(text=self.query(sql)[0][0])

        eb = self.query("SELECT COUNT(*) FROM produtos WHERE quantidade_minima>0 AND quantidade<=quantidade_minima")[0][0]
        self.cards["Estoque Baixo"].config(text=str(eb), fg=COR_PERIGO if eb > 0 else COR_SUCESSO)
        total = self.query("SELECT SUM(quantidade*preco_venda) FROM produtos")[0][0] or 0
        total_str = f"MT {total:,.2f}".replace(',','X').replace('.',',').replace('X','.')
        self.cards["Valor Total"].config(text=total_str)

        self.desenhar_linha()
        self.desenhar_donut()
        self.desenhar_barras()
        self.atualizar_painel()

    def desenhar_linha(self):
        self.line_canvas.delete("all")
        w = self.line_canvas.winfo_width() or 600
        h = self.line_canvas.winfo_height() or 220
        if w < 50: return

        dias = 30
        dados = []
        for i in range(dias - 1, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            ent = self.query("SELECT COUNT(*) FROM movimentacoes WHERE tipo='entrada' AND data LIKE ?", (d+'%',))[0][0]
            sai = self.query("SELECT COUNT(*) FROM movimentacoes WHERE tipo='saida' AND data LIKE ?", (d+'%',))[0][0]
            dados.append((d, ent, sai))

        max_val = max([max(e, s) for _, e, s in dados] or [1])
        pad = 40
        gw = w - pad - 15
        gh = h - 35
        pontos_ent, pontos_sai = [], []

        for i, (_, ent, sai) in enumerate(dados):
            x = pad + (i / max(dias - 1, 1)) * gw
            y_ent = h - 20 - (ent / max_val) * gh if max_val > 0 else h - 20
            y_sai = h - 20 - (sai / max_val) * gh if max_val > 0 else h - 20
            pontos_ent.append((x, y_ent))
            pontos_sai.append((x, y_sai))

        for pts, cor in [(pontos_ent, COR_SUCESSO), (pontos_sai, COR_PERIGO)]:
            for i in range(1, len(pts)):
                if pts[i-1][1] != h - 20 or pts[i][1] != h - 20:
                    self.line_canvas.create_line(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1],
                                                  fill=cor, width=2, smooth=True)
            for i, (x, y) in enumerate(pts):
                if dados[i][1] > 0 or dados[i][2] > 0:
                    r = 3
                    self.line_canvas.create_oval(x - r, y - r, x + r, y + r, fill=cor, outline=COR_BG2, width=1)

        # Linha de grade horizontal
        for i in range(0, 5):
            y = h - 20 - (gh / 4) * i
            self.line_canvas.create_line(pad, y, w - 10, y, fill=COR_BORDA, width=0.5)

        # Eixo Y
        for i in range(0, 5):
            y = h - 20 - (gh / 4) * i
            val = int((max_val / 4) * i)
            self.line_canvas.create_text(pad - 6, y, text=str(val), fill=COR_TEXTO2,
                                          font=("Segoe UI", 7), anchor='e')

        # Eixo X
        for i in range(0, dias, 5):
            x = pad + (i / max(dias - 1, 1)) * gw
            self.line_canvas.create_line(x, h - 20, x, h - 15, fill=COR_BORDA, width=0.5)
            lbl = dados[i][0][5:]
            self.line_canvas.create_text(x, h - 5, text=lbl, fill=COR_TEXTO2, font=("Segoe UI", 7))

        # Legenda
        self.line_canvas.create_rectangle(w - 120, 6, w - 108, 16, fill=COR_SUCESSO, outline="")
        self.line_canvas.create_text(w - 104, 11, text="Entradas", fill=COR_TEXTO2, font=("Segoe UI", 8), anchor='w')
        self.line_canvas.create_rectangle(w - 50, 6, w - 38, 16, fill=COR_PERIGO, outline="")
        self.line_canvas.create_text(w - 34, 11, text="Saídas", fill=COR_TEXTO2, font=("Segoe UI", 8), anchor='w')

    def desenhar_donut(self):
        self.donut_canvas.delete("all")
        w = self.donut_canvas.winfo_width() or 350
        h = self.donut_canvas.winfo_height() or 170
        if w < 50: return

        cats = self.query('''SELECT c.nome, COUNT(p.id) FROM categorias c
            JOIN produtos p ON p.categoria_id=c.id GROUP BY c.id ORDER BY COUNT(p.id) DESC''')
        sem_cat = self.query("SELECT COUNT(*) FROM produtos WHERE categoria_id IS NULL")[0][0]
        todos = list(cats) + ([("Sem cat.", sem_cat)] if sem_cat else [])
        total = sum(r[1] for r in todos) or 1

        cx, cy = 80, h // 2
        raio = 55
        ang = 0
        cores = [COR_PRIMARIA, COR_INFO, COR_SUCESSO, COR_AVISO, COR_PERIGO, COR_ROSA, COR_TEXTO]

        for i, (nome, qtd) in enumerate(todos):
            if qtd == 0: continue
            extent = (qtd / total) * 360
            cor = cores[i % len(cores)]
            self.donut_canvas.create_arc(cx - raio, cy - raio, cx + raio, cy + raio,
                                          start=ang, extent=extent, fill=cor, outline=COR_BG2, width=2)
            ang += extent

        self.donut_canvas.create_oval(cx - 20, cy - 20, cx + 20, cy + 20,
                                       fill=COR_BG2, outline="")
        self.donut_canvas.create_text(cx, cy - 5, text=str(total), fill="white",
                                       font=("Segoe UI", 14, "bold"))
        self.donut_canvas.create_text(cx, cy + 12, text="prod", fill=COR_TEXTO2,
                                       font=("Segoe UI", 8))

        leg_x = 150
        for i, (nome, qtd) in enumerate(todos):
            if qtd == 0: continue
            cor = cores[i % len(cores)]
            y = 10 + i * 20
            self.donut_canvas.create_rectangle(leg_x, y, leg_x + 10, y + 10,
                                                fill=cor, outline="")
            label = f"{nome} ({qtd})" if len(nome) < 15 else f"{nome[:12]}...({qtd})"
            self.donut_canvas.create_text(leg_x + 16, y + 5, text=label, anchor='w',
                                           fill=COR_TEXTO, font=("Segoe UI", 8))

    def desenhar_barras(self):
        self.bars_canvas.delete("all")
        w = self.bars_canvas.winfo_width() or 350
        h = self.bars_canvas.winfo_height() or 170
        if w < 50: return

        prods = self.query("SELECT nome, quantidade FROM produtos ORDER BY quantidade DESC LIMIT 6")
        if not prods:
            self.bars_canvas.create_text(w // 2, h // 2, text="Sem dados", fill=COR_TEXTO2, font=("Segoe UI", 10))
            return

        max_qtd = max(p[1] for p in prods) or 1
        pad = 80
        gw = w - pad - 15
        bar_w = min(40, (gw - 10) // len(prods))
        gap = 8
        total_bw = len(prods) * (bar_w + gap) - gap
        x_start = pad + (gw - total_bw) // 2
        cores = [COR_INFO, COR_PRIMARIA, COR_SUCESSO, COR_AVISO, COR_PERIGO, COR_ROSA]

        for i, (nome, qtd) in enumerate(prods):
            x = x_start + i * (bar_w + gap)
            bh = max(6, (qtd / max_qtd) * (h - 30))
            y = h - 15 - bh
            cor = cores[i % len(cores)]
            self.bars_canvas.create_rectangle(x, y, x + bar_w, h - 15,
                                               fill=cor, outline="", width=0)
            nome_s = nome if len(nome) <= 8 else nome[:7] + "."
            self.bars_canvas.create_text(x + bar_w // 2, h - 3, text=nome_s,
                                          fill=COR_TEXTO2, font=("Segoe UI", 7), anchor='n')
            self.bars_canvas.create_text(x + bar_w // 2, y - 3, text=f"{qtd:.0f}",
                                          fill=cor, font=("Segoe UI", 8, "bold"), anchor='s')

    def atualizar_painel(self):
        for w in self.painel_lista.winfo_children():
            w.destroy()

        hoje = datetime.now().strftime("%Y-%m-%d")
        ent = self.query("SELECT COUNT(*) FROM movimentacoes WHERE tipo='entrada' AND data LIKE ?", (hoje+'%',))[0][0]
        sai = self.query("SELECT COUNT(*) FROM movimentacoes WHERE tipo='saida' AND data LIKE ?", (hoje+'%',))[0][0]

        resumo = tk.Frame(self.painel_lista, bg=COR_BG2, padx=10, pady=8)
        resumo.pack(fill='x')
        tk.Label(resumo, text=datetime.now().strftime("%A, %d/%m/%Y"),
                 font=("Segoe UI", 9, "bold"), bg=COR_BG2, fg=COR_TEXTO).pack(anchor='w')

        for label, val, cor in [
            ("Entradas hoje", ent, COR_SUCESSO),
            ("Saídas hoje", sai, COR_PERIGO),
            ("Total mov.", ent + sai, COR_INFO),
        ]:
            f = tk.Frame(resumo, bg=COR_BG2)
            f.pack(fill='x', pady=2)
            tk.Label(f, text=label, font=("Segoe UI", 9), bg=COR_BG2, fg=COR_TEXTO2).pack(side='left')
            tk.Label(f, text=str(val), font=("Segoe UI", 9, "bold"), bg=COR_BG2, fg=cor).pack(side='right')

        tk.Frame(self.painel_lista, bg=COR_BORDA, height=1).pack(fill='x', pady=5)

        # Indicadores
        indicadores = tk.Frame(self.painel_lista, bg=COR_BG2, padx=10, pady=5)
        indicadores.pack(fill='x')

        items = [
            ("Produtos", self.query("SELECT COUNT(*) FROM produtos")[0][0], COR_PRIMARIA),
            ("Categorias", self.query("SELECT COUNT(*) FROM categorias")[0][0], COR_INFO),
            ("Estoque Baixo", self.query("SELECT COUNT(*) FROM produtos WHERE quantidade_minima>0 AND quantidade<=quantidade_minima")[0][0], COR_PERIGO),
            ("Zerados", self.query("SELECT COUNT(*) FROM produtos WHERE quantidade=0")[0][0], COR_AVISO),
        ]
        for label, val, cor in items:
            f = tk.Frame(indicadores, bg=COR_BG2)
            f.pack(fill='x', pady=1)
            tk.Label(f, text=label, font=("Segoe UI", 9), bg=COR_BG2, fg=COR_TEXTO2).pack(side='left')
            tk.Label(f, text=str(val), font=("Segoe UI", 9, "bold"), bg=COR_BG2, fg=cor).pack(side='right')

        # Últimas movimentações
        ultimas = self.query('''SELECT m.data, p.nome, m.tipo, printf('%.1f',m.quantidade)
            FROM movimentacoes m JOIN produtos p ON m.produto_id=p.id
            ORDER BY m.data DESC LIMIT 5''')
        if ultimas:
            tk.Frame(self.painel_lista, bg=COR_BORDA, height=1).pack(fill='x', pady=5)
            tk.Label(self.painel_lista, text="Últimas", font=("Segoe UI", 8, "bold"),
                     bg=COR_BG2, fg=COR_TEXTO2, padx=10).pack(anchor='w')
            for data, nome, tipo, qtd in ultimas:
                f = tk.Frame(self.painel_lista, bg=COR_BG2)
                f.pack(fill='x', padx=10, pady=1)
                cor = COR_SUCESSO if tipo == "entrada" else COR_PERIGO
                lbl_t = tk.Label(f, text="E" if tipo=="entrada" else "S",
                                 font=("Segoe UI", 7, "bold"), bg=cor, fg="white", width=2)
                lbl_t.pack(side='left')
                txt = f"{nome[:14]}  {qtd}" if len(nome) <= 14 else f"{nome[:11]}...{qtd}"
                tk.Label(f, text=txt, font=("Segoe UI", 8), bg=COR_BG2, fg=COR_TEXTO,
                         anchor='w').pack(side='left', fill='x', expand=True, padx=4)
                tk.Label(f, text=data[5:16], font=("Segoe UI", 7),
                         bg=COR_BG2, fg=COR_TEXTO2).pack(side='right')

    def desenhar_donut(self):
        self.donut_canvas.delete("all")
        w = self.donut_canvas.winfo_width() or 400
        h = self.donut_canvas.winfo_height() or 160
        if w < 50: return

        cats = self.query('''SELECT c.nome, COUNT(p.id) FROM categorias c
            JOIN produtos p ON p.categoria_id=c.id GROUP BY c.id ORDER BY COUNT(p.id) DESC''')
        sem_cat = self.query("SELECT COUNT(*) FROM produtos WHERE categoria_id IS NULL")[0][0]

        todos = list(cats) + ([("Sem categoria", sem_cat)] if sem_cat else [])
        total = sum(r[1] for r in todos) if todos else 1

        cx, cy, raio = 90, 80, 60
        cores = [COR_PRIMARIA, COR_INFO, COR_SUCESSO, COR_AVISO, COR_PERIGO, COR_ROSA, COR_TEXTO2]
        ang = 0
        leg_x = 180

        for i, (nome, qtd) in enumerate(todos):
            if qtd == 0: continue
            extent = (qtd / total) * 360
            cor = cores[i % len(cores)]
            self.donut_canvas.create_arc(cx-raio, cy-raio, cx+raio, cy+raio,
                                          start=ang, extent=extent, fill=cor, outline=COR_BG2, width=2)
            ang += extent

            y = 15 + i * 22
            self.donut_canvas.create_rectangle(leg_x, y, leg_x+12, y+12, fill=cor, outline="")
            nome_txt = f"{nome} ({qtd})"
            self.donut_canvas.create_text(leg_x+18, y+6, text=nome_txt, anchor='w',
                                           fill=COR_TEXTO, font=("Segoe UI", 9))

        self.donut_canvas.create_text(cx, cy, text=str(total), fill="white",
                                       font=("Segoe UI", 16, "bold"))
        self.donut_canvas.create_text(cx, cy+16, text="total", fill=COR_TEXTO2,
                                       font=("Segoe UI", 7))

    # ===================== PDV =====================
    def build_pdv(self):
        f = self.tab_pdv
        self.carrinho = []

        topo = tk.Frame(f, bg=COR_BG)
        topo.pack(fill='x', pady=10)
        tk.Label(topo, text="PDV - Ponto de Venda", font=("Segoe UI", 18, "bold"),
                 bg=COR_BG, fg="white").pack(side='left')
        self.pdv_cliente = ttk.Entry(topo, width=20)
        self.pdv_cliente.pack(side='right', padx=5)
        tk.Label(topo, text="Cliente:", font=("Segoe UI", 10), bg=COR_BG,
                 fg=COR_TEXTO2).pack(side='right')

        painel = tk.PanedWindow(f, orient='horizontal', bg=COR_BG, sashwidth=4, sashrelief='sunken')
        painel.pack(fill='both', expand=True)

        esq = tk.Frame(painel, bg=COR_BG)
        dir_ = tk.Frame(painel, bg=COR_BG)

        painel.add(esq, width=580, minsize=400)
        painel.add(dir_, width=450, minsize=320)

        # --- Painel Esquerdo: Busca e Produtos ---
        busca_f = tk.Frame(esq, bg=COR_BG)
        busca_f.pack(fill='x')
        self.pdv_search = ttk.Entry(busca_f, style="Search.TEntry", font=("Segoe UI", 14))
        self.pdv_search.pack(side='left', fill='x', expand=True)
        self.pdv_search.bind('<KeyRelease>', self.update_pdv_produtos)
        self.pdv_search.bind('<Return>', lambda e: self.pdv_add_item())

        cols_prod = ('Código', 'Produto', 'Preço', 'Estoque')
        self.tree_pdv = ttk.Treeview(esq, columns=cols_prod, show='headings', height=14)
        for c, w in zip(cols_prod, [100, 280, 100, 80]):
            self.tree_pdv.heading(c, text=c)
            self.tree_pdv.column(c, width=w, anchor='center')
        self.tree_pdv.heading('Produto', anchor='w')
        self.tree_pdv.column('Produto', anchor='w')
        self.tree_pdv.pack(fill='both', expand=True, pady=8)
        self.tree_pdv.bind('<Double-1>', lambda e: self.pdv_add_item())

        qtd_f = tk.Frame(esq, bg=COR_BG)
        qtd_f.pack(fill='x')
        tk.Label(qtd_f, text="Qtd:", font=("Segoe UI", 12, "bold"), bg=COR_BG,
                 fg=COR_TEXTO).pack(side='left', padx=5)
        self.pdv_qtd = ttk.Spinbox(qtd_f, from_=1, to=9999, width=8, font=("Segoe UI", 12))
        self.pdv_qtd.set(1)
        self.pdv_qtd.pack(side='left')
        ttk.Button(qtd_f, text="\u2795 Adicionar", command=self.pdv_add_item,
                   style="Success.TButton").pack(side='left', padx=15)

        # --- Painel Direito: Carrinho ---
        tk.Label(dir_, text="Carrinho", font=("Segoe UI", 14, "bold"),
                 bg=COR_BG, fg="white").pack(anchor='w')

        cols_cart = ('Item', 'Qtd', 'Preço', 'Total')
        self.tree_cart = ttk.Treeview(dir_, columns=cols_cart, show='headings', height=16)
        for c, w in zip(cols_cart, [220, 60, 80, 100]):
            self.tree_cart.heading(c, text=c)
            self.tree_cart.column(c, width=w, anchor='center')
        self.tree_cart.heading('Item', anchor='w')
        self.tree_cart.column('Item', anchor='w')
        self.tree_cart.pack(fill='both', expand=True, pady=5)

        cart_btn = tk.Frame(dir_, bg=COR_BG)
        cart_btn.pack(fill='x')
        ttk.Button(cart_btn, text="\u2796 Remover", command=self.pdv_remover_item,
                   style="Danger.TButton").pack(side='left', padx=2)
        ttk.Button(cart_btn, text="\U0001f5d1 Limpar", command=self.pdv_limpar_carrinho,
                   style="Outline.TButton").pack(side='left', padx=2)

        total_f = tk.Frame(dir_, bg=COR_BG, bd=2, relief='solid', highlightbackground=COR_PRIMARIA)
        total_f.pack(fill='x', pady=8, ipady=6)
        self.pdv_total_var = tk.StringVar(value="0,00 MT")
        tk.Label(total_f, text="TOTAL:", font=("Segoe UI", 14, "bold"), bg=COR_BG,
                 fg=COR_TEXTO).pack(side='left', padx=10)
        tk.Label(total_f, textvariable=self.pdv_total_var, font=("Segoe UI", 20, "bold"),
                 bg=COR_BG, fg=COR_SUCESSO).pack(side='right', padx=10)

        pag_f = tk.Frame(dir_, bg=COR_BG)
        pag_f.pack(fill='x')
        self.pdv_pag = ttk.Combobox(pag_f, values=["Dinheiro", "Cartão Débito", "Cartão Crédito", "Transferência", "Faturar"],
                                    state='readonly', width=16, font=("Segoe UI", 10))
        self.pdv_pag.set("Dinheiro")
        self.pdv_pag.pack(side='left', padx=2)
        ttk.Button(pag_f, text="\U0001f4b3 Finalizar Venda", command=self.pdv_finalizar,
                   style="Success.TButton").pack(side='left', padx=5)

        self.update_pdv_produtos()

    def update_pdv_produtos(self, *_):
        busca = self.pdv_search.get().strip() if hasattr(self, 'pdv_search') else ""
        busca_normal = remover_acentos(busca) if busca else ""
        sql = '''SELECT IFNULL(p.codigo_barras,'-'), p.nome,
            printf('%.2f',p.preco_venda), printf('%.2f',p.quantidade)
            FROM produtos p ORDER BY p.nome'''
        dados = self.query(sql)
        if busca_normal:
            dados = [r for r in dados if busca_normal in remover_acentos(r[1]) or
                     busca_normal in remover_acentos(r[0])]
        for r in self.tree_pdv.get_children():
            self.tree_pdv.delete(r)
        for row in dados:
            self.tree_pdv.insert('', 'end', values=row)

    def pdv_add_item(self):
        sel = self.tree_pdv.selection()
        if not sel:
            busca = self.pdv_search.get().strip()
            if busca:
                self.pdv_search.focus()
                self.pdv_search.select_range(0, 'end')
            return
        v = self.tree_pdv.item(sel[0])['values']
        nome = v[1]
        try:
            preco = float(v[2].replace('.','').replace(',','.'))
        except:
            messagebox.showwarning("Erro", "Preço inválido"); return
        try:
            qtd = float(self.pdv_qtd.get().replace(',','.'))
        except:
            messagebox.showwarning("Erro", "Quantidade inválida"); return
        if qtd <= 0:
            messagebox.showwarning("Erro", "Quantidade deve ser > 0"); return
        try:
            estoque = float(v[3])
        except:
            estoque = 0
        if qtd > estoque:
            if not messagebox.askyesno("Aviso", f"Estoque insuficiente! Tem {estoque:.0f} unidades. Continuar?"):
                return

        self.carrinho.append([nome, qtd, preco, qtd * preco])
        self.pdv_qtd.set(1)
        self.pdv_search.focus()
        self._atualizar_carrinho()

    def pdv_remover_item(self):
        sel = self.tree_cart.selection()
        if not sel: return
        idx = self.tree_cart.index(sel[0])
        self.carrinho.pop(idx)
        self._atualizar_carrinho()

    def pdv_limpar_carrinho(self):
        if not self.carrinho: return
        self.carrinho.clear()
        self._atualizar_carrinho()

    def _atualizar_carrinho(self):
        for r in self.tree_cart.get_children():
            self.tree_cart.delete(r)
        total = 0
        for item, qtd, preco, subtotal in self.carrinho:
            self.tree_cart.insert('', 'end', values=(
                item,
                f"{qtd:.0f}" if qtd == int(qtd) else f"{qtd:.2f}",
                f"{preco:,.2f}".replace(',',' ').replace('.',',').replace(' ', '.'),
                f"{subtotal:,.2f}".replace(',',' ').replace('.',',').replace(' ', '.'),
            ))
            total += subtotal
        self.pdv_total_var.set(
            f"{total:,.2f} MT".replace(',',' ').replace('.',',').replace(' ', '.'))

    def pdv_finalizar(self):
        if not self.carrinho:
            messagebox.showwarning("Carrinho vazio", "Adicione produtos ao carrinho"); return
        total = sum(s for _,_,_,s in self.carrinho)
        pag = self.pdv_pag.get()
        cliente = self.pdv_cliente.get().strip() or "Consumidor Final"
        msg = f"Cliente: {cliente}\nForma Pag.: {pag}\n\nItens:\n"
        for item, qtd, preco, _ in self.carrinho:
            msg += f"  {item} x{qtd} @ {preco:,.2f} MT\n".replace(',',' ').replace('.',',').replace(' ', '.')
        msg += f"\nTOTAL: {total:,.2f} MT".replace(',',' ').replace('.',',').replace(' ', '.')

        if not messagebox.askyesno("Confirmar Venda", msg):
            return

        erros = []
        for item, qtd, preco, _ in self.carrinho:
            prod = self.query("SELECT id FROM produtos WHERE nome=?", (item,))
            if not prod:
                erros.append(f"Produto '{item}' não encontrado")
                continue
            pid = prod[0][0]
            self.query("UPDATE produtos SET quantidade = quantidade - ? WHERE id=?", (qtd, pid))
            self.query('''INSERT INTO movimentacoes (produto_id,tipo,quantidade,preco_unitario,documento,observacao)
                VALUES (?,?,?,?,?,?)''', (pid, "saida", qtd, preco, "PDV", f"Venda {cliente}"))

        if erros:
            messagebox.showwarning("Erros", "\n".join(erros))
        else:
            messagebox.showinfo("Venda Concluída",
                f"Venda de {total:,.2f} MT registrada!\nPagamento: {pag}".replace(',',' ').replace('.',',').replace(' ', '.'))

        self.carrinho.clear()
        self._atualizar_carrinho()
        self.update_pdv_produtos()
        self.update_produtos()
        self.update_dashboard()

    # ===================== PRODUTOS =====================
    def build_produtos(self):
        f = self.tab_produtos

        topo = tk.Frame(f, bg=COR_BG)
        topo.pack(fill='x', pady=10)
        tk.Label(topo, text="Produtos", font=("Segoe UI", 18, "bold"),
                 bg=COR_BG, fg="white").pack(side='left')

        botoes = tk.Frame(topo, bg=COR_BG)
        botoes.pack(side='right')
        ttk.Button(botoes, text="+ Novo", command=self.produto_form, style="Success.TButton").pack(side='left', padx=2)
        ttk.Button(botoes, text="Editar", command=lambda: self.produto_form(self.get_selected(self.tree_prod, 0))).pack(side='left', padx=2)
        ttk.Button(botoes, text="Excluir", command=self.excluir_produto, style="Danger.TButton").pack(side='left', padx=2)
        ttk.Button(botoes, text="CSV", command=lambda: self.exportar_tree(self.tree_prod, "produtos"), style="Outline.TButton").pack(side='left', padx=2)

        busca_f = tk.Frame(f, bg=COR_BG)
        busca_f.pack(fill='x', pady=(0, 8))
        tk.Label(busca_f, text="\U0001f50d", font=("Segoe UI", 12), bg=COR_BG, fg=COR_TEXTO2).pack(side='left')
        self.prod_search = ttk.Entry(busca_f, style="Search.TEntry")
        self.prod_search.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.prod_search.bind("<KeyRelease>", lambda e: self.update_produtos())

        cols = ('ID', 'Nome', 'Código', 'Categoria', 'Qtd', 'Min', 'Custo', 'Venda', 'Un')
        prod_tree_frame = tk.Frame(f, bg=COR_BG)
        prod_tree_frame.pack(fill='both', expand=True)
        self.tree_prod = ttk.Treeview(prod_tree_frame, columns=cols, show='headings', height=18)
        for c, w in zip(cols, [40, 200, 80, 120, 75, 60, 80, 80, 50]):
            self.tree_prod.heading(c, text=c)
            self.tree_prod.column(c, width=w, anchor='center')
        self.tree_prod.heading('Nome', anchor='w')
        self.tree_prod.column('Nome', anchor='w')
        scroll_prod = ttk.Scrollbar(prod_tree_frame, orient='vertical', command=self.tree_prod.yview)
        self.tree_prod.configure(yscrollcommand=scroll_prod.set)
        self.tree_prod.pack(side='left', fill='both', expand=True)
        scroll_prod.pack(side='right', fill='y')
        self.tree_prod.bind("<Double-1>", lambda e: self.produto_form(self.get_selected(self.tree_prod, 0, True)))
        self.tree_prod.tag_configure('eb', background="#2d1b1b")
        self.update_produtos()

    def update_produtos(self, *_):
        busca = self.prod_search.get().strip() if hasattr(self, 'prod_search') else ""
        busca_normal = remover_acentos(busca) if busca else ""
        sql = '''SELECT p.id, p.nome, IFNULL(p.codigo_barras,'-'), IFNULL(c.nome,'-'),
            printf('%.2f',p.quantidade), printf('%.2f',p.quantidade_minima),
            printf('%.2f',p.preco_custo), printf('%.2f',p.preco_venda), p.unidade
            FROM produtos p LEFT JOIN categorias c ON p.categoria_id=c.id ORDER BY p.nome'''
        dados = self.query(sql)
        if busca_normal:
            dados = [r for r in dados if busca_normal in remover_acentos(r[1]) or
                     busca_normal in remover_acentos(r[2]) or
                     busca_normal in remover_acentos(r[3])]
        for row in self.tree_prod.get_children():
            self.tree_prod.delete(row)
        for row in dados:
            self.tree_prod.insert('', 'end', values=row)
        for row in self.tree_prod.get_children():
            v = self.tree_prod.item(row)['values']
            try:
                if v[5] and float(v[5]) > 0 and float(v[4]) <= float(v[5]):
                    self.tree_prod.item(row, tags=('eb',))
            except: pass

    def produto_form(self, prod_id=None):
        win = tk.Toplevel(self.root)
        win.title("Produto")
        win.geometry("600x600")
        win.configure(bg=COR_BG)

        data = {}
        if prod_id:
            r = self.query("SELECT * FROM produtos WHERE id=?", (prod_id,))
            if r: data = r[0]

        main = tk.Frame(win, bg=COR_BG, padx=20, pady=15)
        main.pack(fill='both', expand=True)

        tk.Label(main, text="Novo Produto" if not prod_id else "Editar Produto",
                 font=("Segoe UI", 16, "bold"), bg=COR_BG, fg="white").pack(anchor='w', pady=(0, 12))

        idx_map = {"nome":1,"codigo":2,"desc":3,"cat":4,"qtd":5,"qtd_min":6,"custo":7,"venda":8,"un":9}
        fields = {}
        rows = [("Nome*","nome"),("Código de Barras","codigo"),("Descrição","desc"),
                ("Categoria","cat"),("Quantidade","qtd"),("Qtd. Mínima","qtd_min"),
                ("Preço Custo (MT)","custo"),("Preço Venda (MT)","venda"),("Unidade","un")]

        for i, (label, key) in enumerate(rows):
            f = tk.Frame(main, bg=COR_BG)
            f.pack(fill='x', pady=3)
            tk.Label(f, text=label, font=("Segoe UI", 10), bg=COR_BG, fg=COR_TEXTO2,
                     width=16, anchor='w').pack(side='left')
            if key == "cat":
                cats = self.query("SELECT id, nome FROM categorias ORDER BY nome")
                var = tk.StringVar()
                w = ttk.Combobox(f, textvariable=var, values=[""]+[c[1] for c in cats], state='readonly')
                fields[key] = (var, w, cats)
            elif key == "un":
                var = tk.StringVar(value="UN")
                w = ttk.Combobox(f, textvariable=var, values=["UN","KG","L","M","CX","PCT","MT","PAR"], state='readonly')
                fields[key] = (var, w)
            else:
                w = ttk.Entry(f)
                fields[key] = w
            w.pack(side='left', fill='x', expand=True, padx=5)
            if data:
                if key == "cat" and data[4]:
                    for c in cats:
                        if c[0] == data[4]: var.set(c[1])
                elif key == "un": var.set(data[9] or "UN")
                elif isinstance(w, ttk.Entry):
                    idx = idx_map[key]
                    w.insert(0, str(data[idx]) if idx < len(data) and data[idx] is not None else "")

        def save():
            nome = fields['nome'].get().strip()
            if not nome: messagebox.showwarning("Aviso", "Nome é obrigatório"); return
            codigo = fields['codigo'].get().strip()
            desc = fields['desc'].get().strip()
            cat_nome = fields['cat'][0].get()
            cat_id = None
            for c in fields['cat'][2]:
                if c[1] == cat_nome: cat_id = c[0]; break
            un = fields['un'][0].get() or "UN"

            def g(v, d=0):
                try: return float(v.get().replace('.','').replace(',','.') or str(d))
                except: return d

            if prod_id:
                self.query('''UPDATE produtos SET nome=?,codigo_barras=?,descricao=?,categoria_id=?,
                    quantidade_minima=?,preco_custo=?,preco_venda=?,unidade=? WHERE id=?''',
                    (nome, codigo, desc, cat_id, g(fields['qtd_min']), g(fields['custo']),
                     g(fields['venda']), un, prod_id))
            else:
                self.query('''INSERT INTO produtos (nome,codigo_barras,descricao,categoria_id,quantidade,
                    quantidade_minima,preco_custo,preco_venda,unidade) VALUES (?,?,?,?,?,?,?,?,?)''',
                    (nome, codigo, desc, cat_id, g(fields['qtd']), g(fields['qtd_min']),
                     g(fields['custo']), g(fields['venda']), un))
            win.destroy()
            self.update_produtos()
            self.update_dashboard()

        bf = tk.Frame(main, bg=COR_BG)
        bf.pack(pady=15)
        ttk.Button(bf, text="Salvar", command=save, style="Success.TButton").pack(side='left', padx=5)
        ttk.Button(bf, text="Cancelar", command=win.destroy, style="Outline.TButton").pack(side='left', padx=5)

    def excluir_produto(self):
        sel = self.get_selected(self.tree_prod, 0)
        if not sel: return
        if messagebox.askyesno("Confirmar", "Excluir produto?"):
            if self.query("SELECT COUNT(*) FROM movimentacoes WHERE produto_id=?", (sel,))[0][0] > 0:
                messagebox.showwarning("Aviso", "Produto com movimentações não pode ser excluído"); return
            self.query("DELETE FROM produtos WHERE id=?", (sel,))
            self.update_produtos()
            self.update_dashboard()

    # ===================== MOVIMENTAÇÕES =====================
    def build_movimentacoes(self):
        f = self.tab_movimentacoes
        topo = tk.Frame(f, bg=COR_BG)
        topo.pack(fill='x', pady=10)
        tk.Label(topo, text="Movimentações", font=("Segoe UI", 18, "bold"),
                 bg=COR_BG, fg="white").pack(side='left')
        botoes = tk.Frame(topo, bg=COR_BG)
        botoes.pack(side='right')
        ttk.Button(botoes, text="+ Entrada", command=lambda: self.mov_form("entrada"), style="Success.TButton").pack(side='left', padx=2)
        ttk.Button(botoes, text="- Saída", command=lambda: self.mov_form("saida"), style="Danger.TButton").pack(side='left', padx=2)
        ttk.Button(botoes, text="Excluir", command=self.excluir_mov, style="Danger.TButton").pack(side='left', padx=2)
        ttk.Button(botoes, text="CSV", command=lambda: self.exportar_tree(self.tree_mov, "movimentacoes"), style="Outline.TButton").pack(side='left', padx=2)

        busca_f = tk.Frame(f, bg=COR_BG)
        busca_f.pack(fill='x', pady=(0, 8))
        tk.Label(busca_f, text="\U0001f50d", font=("Segoe UI", 12), bg=COR_BG, fg=COR_TEXTO2).pack(side='left')
        self.mov_search = ttk.Entry(busca_f, style="Search.TEntry")
        self.mov_search.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.mov_search.bind("<KeyRelease>", lambda e: self.update_movimentacoes())

        cols = ('ID', 'Data', 'Produto', 'Tipo', 'Qtd', 'Preço Unit.', 'Documento', 'Obs')
        mov_tree_frame = tk.Frame(f, bg=COR_BG)
        mov_tree_frame.pack(fill='both', expand=True)
        self.tree_mov = ttk.Treeview(mov_tree_frame, columns=cols, show='headings', height=18)
        for c, w in zip(cols, [40, 130, 200, 80, 100, 90, 100, 150]):
            self.tree_mov.heading(c, text=c)
            self.tree_mov.column(c, width=w, anchor='center')
        self.tree_mov.heading('Produto', anchor='w')
        self.tree_mov.column('Produto', anchor='w')
        scroll_mov = ttk.Scrollbar(mov_tree_frame, orient='vertical', command=self.tree_mov.yview)
        self.tree_mov.configure(yscrollcommand=scroll_mov.set)
        self.tree_mov.pack(side='left', fill='both', expand=True)
        scroll_mov.pack(side='right', fill='y')
        self.tree_mov.tag_configure('entrada', foreground=COR_SUCESSO)
        self.tree_mov.tag_configure('saida', foreground=COR_PERIGO)

    def update_movimentacoes(self, *_):
        busca = self.mov_search.get().strip() if hasattr(self, 'mov_search') else ""
        busca_normal = remover_acentos(busca) if busca else ""
        sql = '''SELECT m.id, m.data, p.nome, m.tipo,
            printf('%.2f',m.quantidade)||' '||p.unidade,
            printf('%.2f',m.preco_unitario), IFNULL(m.documento,'-'), IFNULL(m.observacao,'-')
            FROM movimentacoes m JOIN produtos p ON m.produto_id=p.id ORDER BY m.data DESC'''
        dados = self.query(sql)
        if busca_normal:
            dados = [r for r in dados if busca_normal in remover_acentos(r[2]) or
                     busca_normal in remover_acentos(r[6]) or
                     busca_normal in remover_acentos(r[7])]
        for row in self.tree_mov.get_children():
            self.tree_mov.delete(row)
        for row in dados:
            self.tree_mov.insert('', 'end', values=row)
        for row in self.tree_mov.get_children():
            tp = self.tree_mov.item(row)['values'][3]
            self.tree_mov.item(row, tags=(tp,))

    def mov_form(self, tipo):
        win = tk.Toplevel(self.root)
        win.title(f"Nova {tipo.title()}")
        win.geometry("500x370")
        win.configure(bg=COR_BG)

        prods = self.query("SELECT id, nome FROM produtos ORDER BY nome")
        if not prods:
            messagebox.showwarning("Aviso", "Cadastre produtos primeiro"); win.destroy(); return

        main = tk.Frame(win, bg=COR_BG, padx=20, pady=15)
        main.pack(fill='both', expand=True)

        cor_t = COR_SUCESSO if tipo=="entrada" else COR_PERIGO
        tk.Label(main, text=f"Nova {tipo.title()}", font=("Segoe UI", 16, "bold"),
                 bg=COR_BG, fg=cor_t).pack(anchor='w', pady=(0, 12))

        tk.Label(main, text="Produto*", font=("Segoe UI", 10), bg=COR_BG, fg=COR_TEXTO2).pack(anchor='w')
        prod_var = tk.StringVar()
        prod_cb = ttk.Combobox(main, textvariable=prod_var, values=[p[1] for p in prods], state='readonly')
        prod_cb.pack(fill='x', pady=(2, 8))

        def add_campo(label):
            f = tk.Frame(main, bg=COR_BG)
            f.pack(fill='x', pady=3)
            tk.Label(f, text=label, font=("Segoe UI", 10), bg=COR_BG, fg=COR_TEXTO2,
                     width=16, anchor='w').pack(side='left')
            e = ttk.Entry(f)
            e.pack(side='left', fill='x', expand=True, padx=5)
            return e

        qtd_e = add_campo("Quantidade*")
        preco_e = add_campo("Preço Unitário (MT)")
        doc_e = add_campo("Documento")
        obs_e = add_campo("Observação")

        def save():
            if not prod_var.get() or not qtd_e.get().strip():
                messagebox.showwarning("Aviso", "Preencha produto e quantidade"); return
            prod_id = next((p[0] for p in prods if p[1] == prod_var.get()), None)
            try: qtd = float(qtd_e.get().replace('.','').replace(',','.'))
            except: messagebox.showwarning("Aviso", "Quantidade inválida"); return
            try: preco = float(preco_e.get().replace('.','').replace(',','.') or "0")
            except: preco = 0

            if tipo == "saida":
                estoque = self.query("SELECT quantidade FROM produtos WHERE id=?", (prod_id,))[0][0]
                if qtd > estoque:
                    messagebox.showwarning("Aviso", f"Estoque insuficiente! Disponível: {estoque:.2f}"); return

            delta = qtd if tipo == "entrada" else -qtd
            self.query("UPDATE produtos SET quantidade = quantidade + ? WHERE id=?", (delta, prod_id))
            self.query('''INSERT INTO movimentacoes (produto_id,tipo,quantidade,preco_unitario,documento,observacao)
                VALUES (?,?,?,?,?,?)''', (prod_id, tipo, qtd, preco, doc_e.get().strip(), obs_e.get().strip()))
            win.destroy()
            self.update_movimentacoes()
            self.update_produtos()
            self.update_dashboard()

        bf = tk.Frame(main, bg=COR_BG)
        bf.pack(pady=15)
        ttk.Button(bf, text="Registrar", command=save,
                   style="Success.TButton" if tipo=="entrada" else "Danger.TButton").pack(side='left', padx=5)
        ttk.Button(bf, text="Cancelar", command=win.destroy, style="Outline.TButton").pack(side='left', padx=5)

    def excluir_mov(self):
        sel = self.get_selected(self.tree_mov, 0)
        if not sel: return
        if messagebox.askyesno("Confirmar", "Excluir movimentação?"):
            r = self.query("SELECT produto_id, tipo, quantidade FROM movimentacoes WHERE id=?", (sel,))
            if r:
                delta = -r[0][2] if r[0][1] == "entrada" else r[0][2]
                self.query("UPDATE produtos SET quantidade = quantidade + ? WHERE id=?", (delta, r[0][0]))
                self.query("DELETE FROM movimentacoes WHERE id=?", (sel,))
                self.update_movimentacoes()
                self.update_produtos()
                self.update_dashboard()

    # ===================== CATEGORIAS =====================
    def build_categorias(self):
        f = self.tab_categorias
        topo = tk.Frame(f, bg=COR_BG)
        topo.pack(fill='x', pady=10)
        tk.Label(topo, text="Categorias", font=("Segoe UI", 18, "bold"),
                 bg=COR_BG, fg="white").pack(side='left')

        form = tk.Frame(f, bg=COR_BG2, padx=15, pady=12)
        form.pack(fill='x')
        tk.Label(form, text="Nome:", font=("Segoe UI", 10), bg=COR_BG2, fg=COR_TEXTO2).pack(side='left')
        self.cat_entry = ttk.Entry(form, width=22)
        self.cat_entry.pack(side='left', padx=5)
        tk.Label(form, text="Descrição:", font=("Segoe UI", 10), bg=COR_BG2, fg=COR_TEXTO2).pack(side='left')
        self.cat_desc = ttk.Entry(form, width=28)
        self.cat_desc.pack(side='left', padx=5)
        ttk.Button(form, text="Adicionar", command=self.add_categoria, style="Success.TButton").pack(side='left', padx=2)
        ttk.Button(form, text="Excluir", command=self.excluir_categoria, style="Danger.TButton").pack(side='left', padx=2)
        ttk.Button(form, text="⟳ Recarregar", command=self.update_categorias, style="Outline.TButton").pack(side='left', padx=2)

        cols = ('ID', 'Nome', 'Descrição', 'Qtd Produtos')
        tree_frame = tk.Frame(f, bg=COR_BG)
        tree_frame.pack(fill='both', expand=True, pady=10)
        self.tree_cat = ttk.Treeview(tree_frame, columns=cols, show='headings', height=16)
        for c, w in zip(cols, [40, 200, 300, 100]):
            self.tree_cat.heading(c, text=c)
            self.tree_cat.column(c, width=w, anchor='center')
        scroll_cat = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_cat.yview)
        self.tree_cat.configure(yscrollcommand=scroll_cat.set)
        self.tree_cat.pack(side='left', fill='both', expand=True)
        scroll_cat.pack(side='right', fill='y')
        self.update_categorias()

    def update_categorias(self):
        dados = self.query('''SELECT c.id, c.nome, IFNULL(c.descricao,'-'),
            (SELECT COUNT(*) FROM produtos p WHERE p.categoria_id=c.id)
            FROM categorias c ORDER BY c.nome''')
        for r in self.tree_cat.get_children():
            self.tree_cat.delete(r)
        for row in dados:
            self.tree_cat.insert('', 'end', values=row)
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"{len(dados)} categorias carregadas")

    def add_categoria(self):
        nome = self.cat_entry.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Digite um nome para a categoria"); return
        try:
            self.query("INSERT INTO categorias (nome,descricao) VALUES (?,?)", (nome, self.cat_desc.get().strip()))
            self.cat_entry.delete(0, 'end')
            self.cat_desc.delete(0, 'end')
            self.update_categorias()
            self.update_dashboard()
            self.status_label.config(text=f"Categoria '{nome}' adicionada")
        except Exception as e:
            messagebox.showwarning("Aviso", f"Não foi possível adicionar: {e}")

    def excluir_categoria(self):
        sel = self.get_selected(self.tree_cat, 0)
        if not sel: return
        if self.query("SELECT COUNT(*) FROM produtos WHERE categoria_id=?", (sel,))[0][0] > 0:
            messagebox.showwarning("Aviso", "Categoria com produtos não pode ser excluída"); return
        self.query("DELETE FROM categorias WHERE id=?", (sel,))
        self.update_categorias()
        self.update_dashboard()

    # ===================== RELATÓRIOS =====================
    def build_relatorios(self):
        f = self.tab_relatorios
        tk.Label(f, text="Relatórios", font=("Segoe UI", 18, "bold"),
                 bg=COR_BG, fg="white").pack(anchor='w', pady=(15, 2))
        tk.Label(f, text="Exporte e visualize dados do estoque", font=("Segoe UI", 10),
                 bg=COR_BG, fg=COR_TEXTO2).pack(anchor='w')

        rels = [
            ("Estoque Baixo", "Produtos abaixo do mínimo", self.rel_estoque_baixo, COR_PERIGO, "\u26a0\ufe0f"),
            ("Mov. por Período", "Filtrar por data", self.rel_mov_periodo, COR_INFO, "\U0001f4c5"),
            ("Todos Produtos", "Listagem completa", self.rel_todos_produtos, COR_PRIMARIA, "\U0001f4e6"),
            ("Valor em Estoque", "Custo total investido", self.rel_valor_estoque, COR_AVISO, "\U0001f4b0"),
        ]

        c_frame = tk.Frame(f, bg=COR_BG)
        c_frame.pack(fill='x', pady=15)

        for titulo, desc, cmd, cor, icone in rels:
            card = tk.Frame(c_frame, bg=COR_BG2, highlightbackground=COR_BORDA,
                            highlightthickness=1, cursor="hand2")
            card.pack(side='left', fill='both', expand=True, padx=4, pady=4, ipadx=5, ipady=8)
            for widget in [card]:
                widget.bind("<Button-1>", lambda e, c=cmd: c())

            acento = tk.Frame(card, bg=cor, height=3)
            acento.pack(fill='x')
            acento.bind("<Button-1>", lambda e, c=cmd: c())

            inner = tk.Frame(card, bg=COR_BG2, padx=14, pady=10)
            inner.pack(fill='both', expand=True)
            inner.bind("<Button-1>", lambda e, c=cmd: c())

            tk.Label(inner, text=icone, font=("Segoe UI", 20), bg=COR_BG2, fg=cor).pack(anchor='w')
            tk.Label(inner, text=titulo, font=("Segoe UI", 12, "bold"),
                     bg=COR_BG2, fg=cor).pack(anchor='w', pady=(3, 2))
            tk.Label(inner, text=desc, font=("Segoe UI", 9),
                     bg=COR_BG2, fg=COR_TEXTO2).pack(anchor='w')

    def exportar_tree(self, tree, nome):
        cab = [tree.heading(c)['text'] for c in tree['columns']]
        dados = []
        for row in tree.get_children():
            dados.append(list(tree.item(row)['values']))
        if dados:
            exportar_csv(dados, cab, nome)

    def rel_estoque_baixo(self):
        win = self.janela_resultado("Estoque Baixo", 750, 450)
        r = self.query('''SELECT p.nome, IFNULL(c.nome,'-'), printf('%.2f',p.quantidade),
            printf('%.2f',p.quantidade_minima), p.unidade
            FROM produtos p LEFT JOIN categorias c ON p.categoria_id=c.id
            WHERE p.quantidade_minima>0 AND p.quantidade<=p.quantidade_minima ORDER BY p.nome''')
        cols = ('Produto', 'Categoria', 'Qtd Atual', 'Mínimo', 'Un')
        tree = self.criar_tree(win, cols, r, [200, 150, 100, 80, 60])
        if not r: messagebox.showinfo("Info", "Nenhum produto com estoque baixo")
        else: ttk.Button(win, text="Exportar CSV", command=lambda: exportar_csv(r, cols, "estoque_baixo"),
                         style="Outline.TButton").pack(pady=5)

    def rel_mov_periodo(self):
        win = tk.Toplevel(self.root)
        win.title("Movimentações por Período")
        win.geometry("480x220")
        win.configure(bg=COR_BG)
        main = tk.Frame(win, bg=COR_BG, padx=20, pady=20)
        main.pack(fill='both', expand=True)
        tk.Label(main, text="Filtrar Movimentações", font=("Segoe UI", 14, "bold"),
                 bg=COR_BG, fg="white").pack(anchor='w', pady=(0, 12))

        for txt, entry in [("Data Início:", None), ("Data Fim:", None)]:
            f = tk.Frame(main, bg=COR_BG)
            f.pack(fill='x', pady=4)
            tk.Label(f, text=txt, bg=COR_BG, fg=COR_TEXTO2, width=12, anchor='w').pack(side='left')
            e = ttk.Entry(f, width=22)
            e.pack(side='left')
            if "Início" in txt: inicio = e; e.insert(0, (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d"))
            else: fim = e; e.insert(0, datetime.now().strftime("%Y-%m-%d"))

        def filtrar():
            if not inicio.get() or not fim.get(): return
            r = self.query('''SELECT m.data, p.nome, CASE WHEN m.tipo='entrada' THEN 'ENTRADA' ELSE 'SAÍDA' END,
                printf('%.2f',m.quantidade)||' '||p.unidade, printf('%.2f',m.preco_unitario), IFNULL(m.documento,'-')
                FROM movimentacoes m JOIN produtos p ON m.produto_id=p.id
                WHERE m.data>=? AND m.data<=? ORDER BY m.data DESC''', (inicio.get(), fim.get()+' 23:59:59'))
            win.destroy()
            if not r: messagebox.showinfo("Info", "Nenhuma movimentação no período"); return
            w2 = self.janela_resultado("Movimentações do Período", 850, 450)
            cols = ('Data','Produto','Tipo','Qtd','Preço','Doc')
            self.criar_tree(w2, cols, r, [130, 200, 80, 100, 80, 120])
            ttk.Button(w2, text="Exportar CSV", command=lambda: exportar_csv(r, cols, "mov_periodo"),
                       style="Outline.TButton").pack(pady=5)

        bf = tk.Frame(main, bg=COR_BG)
        bf.pack(pady=12)
        ttk.Button(bf, text="Filtrar", command=filtrar, style="Success.TButton").pack(side='left', padx=5)
        ttk.Button(bf, text="Cancelar", command=win.destroy, style="Outline.TButton").pack(side='left', padx=5)

    def rel_todos_produtos(self):
        win = self.janela_resultado("Todos os Produtos", 950, 500)
        cols = ('ID','Nome','Código','Categoria','Qtd','Min','Custo','Venda','Un')
        r = self.query('''SELECT p.id, p.nome, IFNULL(p.codigo_barras,'-'), IFNULL(c.nome,'-'),
            printf('%.2f',p.quantidade), printf('%.2f',p.quantidade_minima),
            printf('%.2f',p.preco_custo), printf('%.2f',p.preco_venda), p.unidade
            FROM produtos p LEFT JOIN categorias c ON p.categoria_id=c.id ORDER BY p.nome''')
        self.criar_tree(win, cols, r, [40, 200, 80, 120, 70, 60, 80, 80, 50])
        ttk.Button(win, text="Exportar CSV", command=lambda: exportar_csv(r, cols, "todos_produtos"),
                   style="Outline.TButton").pack(pady=5)

    def rel_valor_estoque(self):
        win = self.janela_resultado("Valor em Estoque", 750, 450)
        cols = ('Produto', 'Categoria', 'Qtd', 'Custo Unit.', 'Valor Total', 'Un')
        r = self.query('''SELECT p.nome, IFNULL(c.nome,'-'), printf('%.2f',p.quantidade),
            printf('%.2f',p.preco_custo), printf('%.2f',p.quantidade*p.preco_custo), p.unidade
            FROM produtos p LEFT JOIN categorias c ON p.categoria_id=c.id
            WHERE p.quantidade>0 ORDER BY p.quantidade*p.preco_custo DESC''')
        self.criar_tree(win, cols, r, [200, 130, 80, 90, 100, 50])
        if not r: messagebox.showinfo("Info", "Nenhum produto em estoque")
        else: ttk.Button(win, text="Exportar CSV", command=lambda: exportar_csv(r, cols, "valor_estoque"),
                         style="Outline.TButton").pack(pady=5)

    def janela_resultado(self, titulo, largura, altura):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry(f"{largura}x{altura}")
        win.configure(bg=COR_BG)
        tk.Label(win, text=titulo, font=("Segoe UI", 14, "bold"),
                 bg=COR_BG, fg="white", padx=15, pady=10).pack(anchor='w')
        return win

    def criar_tree(self, parent, cols, dados, widths):
        f = tk.Frame(parent, bg=COR_BG, padx=10, pady=5)
        f.pack(fill='both', expand=True)
        tree = ttk.Treeview(f, columns=cols, show='headings', height=16)
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor='center')
        tree.heading(cols[0], anchor='w')
        tree.column(cols[0], anchor='w')
        tree.pack(fill='both', expand=True)
        for row in dados:
            tree.insert('', 'end', values=row)
        return tree

    def get_selected(self, tree, col, silent=False):
        sel = tree.selection()
        if not sel:
            if not silent: messagebox.showwarning("Aviso", "Selecione um item")
            return None
        return tree.item(sel[0])['values'][col]

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ControleEstoqueApp(root)
    root.mainloop()
