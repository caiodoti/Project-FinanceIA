import datetime
from db import get_db

def responder_pergunta(user_id, texto):
    texto = texto.lower().strip()
    conn = get_db()
    cur = conn.cursor()
    
    # Pergunta sobre gasto total
    if "quanto gastei" in texto or "total gasto" in texto:
        categoria = None
        for cat in ["mercado", "transporte", "internet", "outros"]:
            if cat in texto:
                categoria = cat
                break
        if categoria:
            cur.execute(
                "SELECT SUM(amount) FROM transactions WHERE user_id=? AND category=?",
                (user_id, categoria)
            )
            total = cur.fetchone()[0] or 0
            conn.close()
            return f"Você gastou R$ {total:.2f} com {categoria}."
        else:
            cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id=?", (user_id,))
            total = cur.fetchone()[0] or 0
            conn.close()
            return f"Seu gasto total até agora é R$ {total:.2f}."
    
    # Resumo do mês
    if "resumo do mês" in texto or "gastos deste mês" in texto:
        hoje = datetime.datetime.now()
        start = hoje.replace(day=1).isoformat()
        cur.execute(
            "SELECT category, SUM(amount) FROM transactions WHERE user_id=? AND date>=? GROUP BY category",
            (user_id, start)
        )
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return "Não há gastos registrados neste mês."
        out = "📆 Resumo deste mês:\n"
        for cat, total in rows:
            out += f"• {cat}: R$ {total:.2f}\n"
        return out
    
    # Maior gasto
    if "maior gasto" in texto or "onde gastei mais" in texto:
        cur.execute(
            "SELECT category, SUM(amount) as total FROM transactions WHERE user_id=? GROUP BY category ORDER BY total DESC LIMIT 1",
            (user_id,)
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return f"Você gastou mais com {row[0]} (R$ {row[1]:.2f})."
        else:
            return "Nenhum gasto registrado ainda."
    
    conn.close()
    return "Desculpe, não consegui entender sua pergunta. Tente algo como: 'quanto gastei no mercado este mês?'"
