class ChartEngine {
    static cores = {
        primary: '#10b981', success: '#22c55e', warning: '#eab308',
        danger: '#ef4444', info: '#0ea5e9', purple: '#14b8a6',
        pink: '#ec4899', orange: '#f97316', teal: '#14b8a6',
        texto: '#e2e8f0', texto2: '#94a3b8', borda: '#334155',
        bg: '#1e293b', bg2: '#0f172a'
    };

    static paleta = [
        '#10b981','#0ea5e9','#eab308','#ef4444','#14b8a6',
        '#ec4899','#06b6d4','#f97316','#34d399','#22c55e',
        '#f43f5e','#38bdf8','#84cc16','#d946ef','#2dd4bf'
    ];

    static _resize(canvas) {
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
        return { ctx, w: rect.width, h: rect.height };
    }

    static _gradiente(ctx, x1, y1, x2, y2, cor1, cor2) {
        const g = ctx.createLinearGradient(x1, y1, x2, y2);
        g.addColorStop(0, cor1);
        g.addColorStop(1, cor2);
        return g;
    }

    static _texto(ctx, txt, x, y, opts = {}) {
        ctx.save();
        ctx.fillStyle = opts.cor || this.cores.texto;
        ctx.font = `${opts.peso||400} ${opts.tam||11}px "Inter",system-ui,sans-serif`;
        ctx.textAlign = opts.align || 'center';
        ctx.textBaseline = opts.baseline || 'middle';
        ctx.fillText(txt, x, y);
        ctx.restore();
    }

    static _formatNum(v) {
        if (v >= 1000000) return (v/1000000).toFixed(1)+'M';
        if (v >= 1000) return (v/1000).toFixed(1)+'k';
        return v.toFixed(0);
    }

    // ─── Bar Chart Vertical ─────────────────────────────────
    static barChart(canvasId, dados, opts = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const { ctx, w, h } = this._resize(canvas);
        const pad = { t: opts.padT||30, r: opts.padR||20, b: opts.padB||50, l: opts.padL||50 };
        const cw = w - pad.l - pad.r;
        const ch = h - pad.t - pad.b;
        const titulo = opts.titulo || '';
        const unit = opts.unidade || '';
        const max = opts.max || Math.max(...dados.map(d => d.valor)) * 1.15;
        const n = dados.length;
        const gap = opts.gap || 0.3;
        const bw = (cw / n) * (1 - gap);
        const rounded = opts.rounded !== false;

        // Clear
        ctx.clearRect(0, 0, w, h);

        // Title
        if (titulo) this._texto(ctx, titulo, w/2, 14, { tam: 13, peso: 600 });

        // Grid
        const linhas = 5;
        ctx.strokeStyle = 'rgba(148,163,184,0.1)';
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 4]);
        for (let i = 0; i <= linhas; i++) {
            const y = pad.t + (ch / linhas) * i;
            ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
            const val = max - (max / linhas) * i;
            this._texto(ctx, this._formatNum(val)+unit, pad.l - 8, y, { cor: this.cores.texto2, align: 'right' });
        }
        ctx.setLineDash([]);

        // Bars
        dados.forEach((d, i) => {
            const x = pad.l + (cw / n) * i + (cw / n) * gap / 2;
            const bh = (d.valor / max) * ch;
            const by = pad.t + ch - bh;
            const cor = d.cor || this.paleta[i % this.paleta.length];

            // Bar with gradient
            const grad = this._gradiente(ctx, x, by, x + bw, by, cor, cor + '88');
            ctx.fillStyle = grad;

            if (rounded && bh > 4) {
                const r = Math.min(4, bh/2);
                ctx.beginPath();
                ctx.moveTo(x + r, by);
                ctx.lineTo(x + bw - r, by);
                ctx.quadraticCurveTo(x + bw, by, x + bw, by + r);
                ctx.lineTo(x + bw, pad.t + ch);
                ctx.lineTo(x, pad.t + ch);
                ctx.lineTo(x, by + r);
                ctx.quadraticCurveTo(x, by, x + r, by);
                ctx.fill();
            } else {
                ctx.fillRect(x, by, bw, bh);
            }

            // Value on top
            if (bh > 20) {
                this._texto(ctx, this._formatNum(d.valor)+unit, x + bw/2, by - 8, { cor: this.cores.texto, tam: 10 });
            }

            // Label
            const lbl = d.label.length > 14 ? d.label.substring(0,12)+'..' : d.label;
            ctx.save();
            ctx.translate(x + bw/2, pad.t + ch + 8);
            ctx.rotate(0);
            ctx.fillStyle = this.cores.texto2;
            ctx.font = '9px "Inter",system-ui,sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            if (n > 8) {
                ctx.save();
                ctx.translate(0, 0);
                ctx.rotate(-0.4);
                ctx.fillText(lbl, 0, 0);
                ctx.restore();
            } else {
                ctx.fillText(lbl, 0, 0);
            }
            ctx.restore();
        });
    }

    // ─── Horizontal Bar Chart ───────────────────────────────
    static hbarChart(canvasId, dados, opts = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const { ctx, w, h } = this._resize(canvas);
        const pad = { t: opts.padT||30, r: opts.padR||30, b: opts.padB||20, l: opts.padL||120 };
        const cw = w - pad.l - pad.r;
        const ch = h - pad.t - pad.b;
        const titulo = opts.titulo || '';
        const unit = opts.unidade || '';
        const max = opts.max || Math.max(...dados.map(d => d.valor)) * 1.1;
        const n = dados.length;
        const gap = opts.gap || 4;
        const rh = Math.min(28, (ch - gap * (n-1)) / n);
        const totalH = n * rh + (n-1) * gap;
        const startY = pad.t + (ch - totalH) / 2;

        ctx.clearRect(0, 0, w, h);
        if (titulo) this._texto(ctx, titulo, w/2, 14, { tam: 13, peso: 600 });

        // Grid lines
        ctx.strokeStyle = 'rgba(148,163,184,0.08)';
        ctx.lineWidth = 1;
        [0.25, 0.5, 0.75, 1].forEach(f => {
            const x = pad.l + cw * f;
            ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, h - pad.b); ctx.stroke();
            this._texto(ctx, this._formatNum(max*f)+unit, x, pad.t - 6, { cor: this.cores.texto2, tam: 9, baseline: 'bottom' });
        });

        dados.forEach((d, i) => {
            const y = startY + i * (rh + gap);
            const bw = (d.valor / max) * cw;
            const cor = d.cor || this.paleta[i % this.paleta.length];

            // Label
            const lbl = d.label.length > 22 ? d.label.substring(0,20)+'..' : d.label;
            this._texto(ctx, lbl, pad.l - 8, y + rh/2, { cor: this.cores.texto2, align: 'right', tam: 10 });

            // Bar
            const grad = this._gradiente(ctx, pad.l, y, pad.l + Math.max(bw, 4), y, cor, cor + '66');
            ctx.fillStyle = grad;
            const r = Math.min(4, rh/2);
            ctx.beginPath();
            ctx.moveTo(pad.l + r, y);
            ctx.lineTo(pad.l + Math.max(bw, r) - r, y);
            ctx.quadraticCurveTo(pad.l + Math.max(bw, r), y, pad.l + Math.max(bw, r), y + r);
            ctx.lineTo(pad.l + Math.max(bw, r), y + rh - r);
            ctx.quadraticCurveTo(pad.l + Math.max(bw, r), y + rh, pad.l + Math.max(bw, r) - r, y + rh);
            ctx.lineTo(pad.l + r, y + rh);
            ctx.quadraticCurveTo(pad.l, y + rh, pad.l, y + rh - r);
            ctx.lineTo(pad.l, y + r);
            ctx.quadraticCurveTo(pad.l, y, pad.l + r, y);
            ctx.fill();

            // Value
            if (bw > 40) {
                this._texto(ctx, this._formatNum(d.valor)+unit, pad.l + bw + 6, y + rh/2, { cor: this.cores.texto, tam: 10, align: 'left' });
            }
        });
    }

    // ─── Pie / Donut Chart ──────────────────────────────────
    static pieChart(canvasId, dados, opts = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const { ctx, w, h } = this._resize(canvas);
        const pad = 20;
        const cx = w / 2, cy = h / 2 + 8;
        const raio = Math.min(w, h) / 2 - pad - (opts.legenda !== false ? 0 : 0);
        const raioInt = opts.donut ? raio * 0.55 : 0;
        const titulo = opts.titulo || '';
        const total = dados.reduce((s, d) => s + d.valor, 0) || 1;

        ctx.clearRect(0, 0, w, h);
        if (titulo) this._texto(ctx, titulo, w/2, 14, { tam: 13, peso: 600 });

        let ang = -Math.PI / 2;
        dados.forEach((d, i) => {
            const frac = d.valor / total;
            const angFim = ang + frac * Math.PI * 2;
            const cor = d.cor || this.paleta[i % this.paleta.length];

            ctx.beginPath();
            if (raioInt > 0) {
                ctx.arc(cx, cy, raioInt, 0, Math.PI * 2);
                ctx.arc(cx, cy, raio, angFim, ang, true);
            } else {
                ctx.moveTo(cx, cy);
                ctx.arc(cx, cy, raio, ang, angFim);
                ctx.closePath();
            }
            ctx.fillStyle = cor;
            ctx.fill();

            // Label on slice
            if (frac > 0.05) {
                const mid = ang + frac * Math.PI;
                const lr = raioInt > 0 ? (raio + raioInt) / 2 : raio * 0.65;
                const lx = cx + Math.cos(mid) * lr;
                const ly = cy + Math.sin(mid) * lr;
                this._texto(ctx, (frac*100).toFixed(0)+'%', lx, ly, { cor: '#fff', tam: 10, peso: 600 });
            }
            ang = angFim;
        });

        // Center text for donut
        if (opts.donut && opts.centro) {
            this._texto(ctx, opts.centro, cx, cy - 6, { cor: this.cores.texto, tam: 18, peso: 700 });
            this._texto(ctx, 'Total', cx, cy + 14, { cor: this.cores.texto2, tam: 10 });
        }

        // Legend
        if (opts.legenda !== false) {
            const lx = 10;
            let ly = h - dados.length * 18 - 8;
            if (dados.length <= 5) ly = Math.max(ly, h - 100);
            dados.forEach((d, i) => {
                const cor = d.cor || this.paleta[i % this.paleta.length];
                ctx.fillStyle = cor;
                ctx.fillRect(lx, ly, 10, 10);
                this._texto(ctx, `${d.label} (${(d.valor/total*100).toFixed(1)}%)`, lx + 16, ly + 5,
                    { cor: this.cores.texto2, align: 'left', tam: 9 });
                ly += 18;
            });
        }
    }

    // ─── Line Chart ─────────────────────────────────────────
    static lineChart(canvasId, datasets, opts = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const { ctx, w, h } = this._resize(canvas);
        const titulo = opts.titulo || '';
        const unit = opts.unidade || '';
        const labels = opts.labels || datasets[0]?.pontos.map((_, i) => i.toString());
        const todosValores = datasets.flatMap(d => d.pontos);
        const max = opts.max || Math.max(...todosValores) * 1.15 || 1;
        const min = opts.min || 0;
        const range = max - min;
        const n = labels.length;
        const area = opts.area !== false;
        const padB = n > 30 ? 54 : (n > 15 ? 46 : 36);
        const pad = { t: opts.padT||30, r: opts.padR||20, b: padB, l: opts.padL||50 };
        const cw = w - pad.l - pad.r;
        const ch = h - pad.t - pad.b;

        ctx.clearRect(0, 0, w, h);
        if (titulo) this._texto(ctx, titulo, w/2, 14, { tam: 13, peso: 600 });

        // Grid
        const linhas = 5;
        ctx.strokeStyle = 'rgba(148,163,184,0.1)';
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 4]);
        for (let i = 0; i <= linhas; i++) {
            const y = pad.t + (ch / linhas) * i;
            ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
            const val = max - (range / linhas) * i;
            this._texto(ctx, this._formatNum(val)+unit, pad.l - 8, y, { cor: this.cores.texto2, align: 'right' });
        }
        ctx.setLineDash([]);

        // X labels
        const step = Math.max(1, Math.floor(n / 10));
        ctx.save();
        ctx.fillStyle = this.cores.texto2;
        ctx.font = '8px "Inter",system-ui,sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        labels.forEach((l, i) => {
            if (i % step !== 0 && i !== n-1) return;
            const x = pad.l + (cw / (n-1 || 1)) * i;
            ctx.save();
            ctx.translate(x, h - pad.b + 6);
            ctx.rotate(n > 15 ? -0.5 : 0);
            ctx.fillText(l, 0, 0);
            ctx.restore();
        });
        ctx.restore();

        // Datasets
        datasets.forEach((ds, di) => {
            const pts = ds.pontos;
            const cor = ds.cor || this.paleta[di % this.paleta.length];
            const pontos = pts.map((v, i) => ({
                x: pad.l + (cw / (n-1 || 1)) * i,
                y: pad.t + ch - ((v - min) / range) * ch
            }));

            // Area fill
            if (area) {
                ctx.beginPath();
                ctx.moveTo(pontos[0].x, pad.t + ch);
                pontos.forEach(p => ctx.lineTo(p.x, p.y));
                ctx.lineTo(pontos[pontos.length-1].x, pad.t + ch);
                ctx.closePath();
                const grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + ch);
                grad.addColorStop(0, cor + '55');
                grad.addColorStop(1, cor + '05');
                ctx.fillStyle = grad;
                ctx.fill();
            }

            // Line
            ctx.beginPath();
            ctx.strokeStyle = cor;
            ctx.lineWidth = 2.5;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';
            pontos.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
            ctx.stroke();

            // Points
            pts.forEach((v, i) => {
                const p = pontos[i];
                ctx.beginPath();
                ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
                ctx.fillStyle = cor;
                ctx.fill();
                ctx.strokeStyle = this.cores.bg;
                ctx.lineWidth = 1.5;
                ctx.stroke();
            });
        });

        // Legend
        if (datasets.length > 1) {
            let lx = w - pad.r - 80;
            const ly = pad.t - 2;
            datasets.forEach((ds, di) => {
                const cor = ds.cor || this.paleta[di % this.paleta.length];
                ctx.fillStyle = cor;
                ctx.fillRect(lx, ly + di * 16, 10, 10);
                this._texto(ctx, ds.label, lx + 14, ly + di * 16 + 5,
                    { cor: this.cores.texto2, align: 'left', tam: 9 });
            });
        }
    }
}
