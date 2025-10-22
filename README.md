# 🤖 WhatsApp Finance Bot com IA Local

Bot financeiro para WhatsApp com IA para análise de gastos.

## ⚙️ Como rodar

1. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Rode o servidor:
   ```bash
   python app.py
   ```

3. Configure o Twilio Sandbox:
   - URL: `http://localhost:3000/webhook` (ou deploy no Render)

4. Comandos no WhatsApp:
   ```
   menu
   meu pin
   adicionar 50 mercado
   resumo <seu PIN>
   saldo <seu PIN>
   simular 1000 10
   quanto gastei no mercado este mês
   maior gasto
   resumo do mês
   ```
