def detectar_intencao(texto: str) -> str:
    texto = texto.lower().strip()
    if any(p in texto for p in ["ajuda", "menu", "opções", "comandos"]):
        return "menu"
    if any(p in texto for p in ["saldo", "quanto tenho", "meu dinheiro"]):
        return "saldo"
    if any(p in texto for p in ["resumo", "gastos", "categorias"]):
        return "resumo"
    if any(p in texto for p in ["simular", "parcelar", "financiamento"]):
        return "simular"
    if any(p in texto for p in ["adicionar", "gaste", "gasto", "comprei", "paguei"]):
        return "adicionar"
    if "pin" in texto:
        return "pin"
    return "desconhecido"
