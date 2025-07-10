# YouTube OBS Manager

## Propósito

Este projeto automatiza a integração entre canais do YouTube e o OBS Studio, permitindo que transmissões ao vivo e eventos agendados de múltiplos canais sejam exibidos automaticamente em fontes de navegador do OBS.

O sistema busca as lives e eventos agendados dos canais configurados, aplica regras especiais (como exibir a live 24h apenas em uma fonte específica), e atualiza as URLs das fontes no OBS via WebSocket. O objetivo é garantir que o OBS sempre mostre a transmissão correta de cada canal, com eficiência de cota da API do YouTube e persistência dos dados.

## Funcionalidades
- Busca automática de lives e eventos agendados no YouTube para cada canal configurado.
- Atualização automática das fontes de navegador no OBS Studio.
- Lógica especial para fontes específicas (ex: live 24h só aparece em uma fonte).
- Persistência dos dados em arquivos JSON diários para evitar buscas desnecessárias na API.
- Log rotativo diário para auditoria e depuração.

## Como usar
1. Configure as variáveis de ambiente com as chaves da API do YouTube, senhas do OBS e IDs dos canais.
2. Execute o script principal (`main.py`).
3. O sistema irá buscar os eventos, atualizar o OBS e salvar os resultados em `pesquisa_api/`.

## Requisitos
- Python 3.8+
- obsws_python
- python-dotenv

## Estrutura
- `app/` — Código principal do sistema
- `pesquisa_api/` — Arquivos de pesquisa diários
- `logs/` — Logs rotativos do sistema

## Observações
- O sistema só faz buscas na API do YouTube uma vez por dia, reutilizando os dados salvos nas execuções seguintes.
- Para forçar uma nova busca, apague o arquivo JSON do dia em `pesquisa_api/`.

---
Desenvolvido para automação de monitoramento de transmissões ao vivo em múltiplos canais do YouTube via OBS Studio.
