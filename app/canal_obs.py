import os
import json
from datetime import datetime as dt, timezone, timedelta

class CanalOBS:
    def __init__(self, channel_id, browser_source_name):
        self.channel_id = channel_id
        self.browser_source_name = browser_source_name
        self.eventos = []
        self.proxima_stream_url = None

    def pasta_pesquisa(self):
        return f"pesquisa_api/{self.browser_source_name.lower().replace('fonte', '')}"  # Exemplo: pesquisa_api/tibagi

    def salvar_pesquisa(self, eventos):
        pasta = self.pasta_pesquisa()
        os.makedirs(pasta, exist_ok=True)
        # Horário do Brasil (Brasília, UTC-3)
        from datetime import timezone, timedelta
        fuso_brasilia = timezone(timedelta(hours=-3))
        data_str = dt.now(fuso_brasilia).strftime("%d-%m-%Y_%H-%M-%S")
        nome_arquivo = os.path.join(pasta, f"{data_str}.json")
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(eventos, f, ensure_ascii=False, indent=2)

    def carregar_ultima_pesquisa(self):
        pasta = self.pasta_pesquisa()
        if not os.path.exists(pasta):
            return []
        arquivos = sorted([f for f in os.listdir(pasta) if f.endswith(".json")])
        if not arquivos:
            return []
        # Filtrar apenas arquivos do dia atual (UTC)
        hoje_str = dt.now(timezone.utc).strftime("%d-%m-%Y")
        arquivos_hoje = [f for f in arquivos if f.startswith(hoje_str)]
        if not arquivos_hoje:
            return []
        nome_arquivo = os.path.join(pasta, arquivos_hoje[-1])
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
