from flask import Flask, request, Response, render_template
from twilio.twiml.messaging_response import MessagingResponse
import re, random, datetime
from db import init_db, get_db
from nlu import detectar_intencao
from ia_financeira import responder_pergunta

app = Flask(__name__)
init_db()

def ensure_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, pin FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        conn.close()
        return {"id": row[0], "pin": row[1]}
    pin = str(random.randint(1000, 9999))
    cur.execute("INSERT INTO users (id, pin) VALUES (?, ?)", (user_id, pin))
    conn.commit()
    conn.close()
    return {"id": user_id, "pin": pin}

def handle_message(user_id, texto):
    conn = get_db()
    cur = conn.cursor()
    texto = texto.strip()
    intencao = detectar_intencao(texto)

    if intencao == "menu":
        return (
            "📋 *Menu Financeiro*\n"
            "1️⃣ saldo <pin> - mostra saldo\n"
            "2️⃣ adicionar <valor> <categoria>\n"
            "3️⃣ resumo <pin>\n"
            "4️⃣ simular <valor> <meses>\n"
            "5️⃣ meu pin\n"
            "_Exemplo:_ adicionar 75 mercado"
        )

    if intencao == "pin":
        cur.execute("SELECT pin FROM users WHERE id = ?", (user_id,))
        pin = cur.fetchone()[0]
        conn.close()
        return f"🔑 Seu PIN: *{pin}*"

    add = re.match(r"(?:adicionar|gaste|paguei|comprei)\s+([0-9]+(?:[.,][0-9]+)?)\s*(.*)", texto.lower())
    if add:
        valor = float(add.group(1).replace(",", "."))
        descricao = add.group(2).strip()
        categoria = descricao.split()[0] if descricao else "outros"
        cur.execute(
            "INSERT INTO transactions (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, valor, categoria, descricao, datetime.datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return f"💰 Registrado: R$ {valor:.2f} em '{categoria}'"

    if intencao == "saldo":
        partes = texto.split()
        if len(partes) < 2:
            conn.close()
            return "Por segurança, envie: *saldo <seu PIN>*"
        pin = partes[1]
        cur.execute("SELECT pin FROM users WHERE id = ?", (user_id,))
        pin_ok = cur.fetchone()[0]
        if pin != pin_ok:
            conn.close()
            return "PIN incorreto ❌"
        cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ?", (user_id,))
        total = cur.fetchone()[0] or 0
        conn.close()
        return f"📊 Seu saldo simulado: R$ {total:.2f}"

    if intencao == "resumo":
        partes = texto.split()
        if len(partes) < 2:
            conn.close()
            return "Envie: *resumo <seu PIN>*"
        pin = partes[1]
        cur.execute("SELECT pin FROM users WHERE id = ?", (user_id,))
        pin_ok = cur.fetchone()[0]
        if pin != pin_ok:
            conn.close()
            return "PIN incorreto ❌"
        start = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
        cur.execute(
            "SELECT category, SUM(amount) FROM transactions WHERE user_id = ? AND date >= ? GROUP BY category",
            (user_id, start)
        )
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return "Sem transações recentes."
        out = "📆 *Resumo 30 dias:*\n"
        for cat, total in rows:
            out += f"• {cat}: R$ {total:.2f}\n"
        return out

    if intencao == "simular":
        sim = re.match(r"(?:simular|parcelar)\s+([0-9]+(?:[.,][0-9]+)?)\s+([0-9]{1,2})", texto)
        if sim:
            valor = float(sim.group(1).replace(",", "."))
            meses = int(sim.group(2))
            juros = 0.12 / 12
            parcela = valor * (juros / (1 - (1 + juros) ** -meses))
            conn.close()
            return f"📈 {meses}x de R$ {parcela:.2f} (total R$ {parcela*meses:.2f})"
        conn.close()
        return "Use: simular <valor> <meses>"

    # IA financeira local
    resposta_ia = responder_pergunta(user_id, texto)
    if "Desculpe, não consegui entender" not in resposta_ia:
        conn.close()
        return resposta_ia

    conn.close()
    return "🤔 Não entendi. Digite *menu*."

@app.route("/webhook", methods=["POST"])
def webhook():
    from_number = request.values.get("From", "")
    body = request.values.get("Body", "")
    ensure_user(from_number)
    resposta = handle_message(from_number, body)
    twiml = MessagingResponse()
    twiml.message(resposta)
    return Response(str(twiml), mimetype="application/xml")

@app.route("/")
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, category, SUM(amount) FROM transactions GROUP BY user_id, category")
    dados = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", dados=dados)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
