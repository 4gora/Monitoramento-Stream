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

1. Crie e configure o arquivo `config.yaml` na raiz do projeto (veja exemplo abaixo).
2. Execute o script principal pelo terminal:
   ```bash
   python3 app/main.py
   ```
3. O programa roda no terminal, exibindo logs em tempo real.
   - Pressione **R** para rodar manualmente uma nova busca e atualização.
   - Pressione **F** para forçar uma busca completa (a pasta `pesquisa_api/` será apagada e todos os dados serão atualizados).
   - Para sair, use **Ctrl+C**.

## Exemplo de config.yaml

```yaml
youtube_api_key: "SUA_CHAVE_API_YOUTUBE"
obs_host: "localhost"         # Opcional, padrão: localhost
obs_port: 4455                # Opcional, padrão: 4455
obs_password: "SENHA_OBS"    # Senha do OBS WebSocket
canais:
  - channel_id: "UCxxxxxxx1" # id do canal do YouTube
    nome: "Canal 1"
  - channel_id: "UCxxxxxxx2"
    nome: "Canal 2"
```



## Requisitos
- Python 3.10+
- OBS Studio 30 ou superior (com WebSocket habilitado)
  - Também funciona em versões anteriores do OBS Studio, desde que o plugin OBS WebSocket esteja instalado manualmente.
- Chave de API para YouTube Data API v3
- Instalar as dependências Python com:
  ```bash
  pip install -r requirements.txt
  ```

## Estrutura
- `app/` — Código principal do sistema
- `pesquisa_api/` — Arquivos de pesquisa diários (gerados automaticamente pelo programa)
- `logs/` — Logs rotativos do sistema (gerados automaticamente pelo programa)
- `config.yaml` — Arquivo de configuração do sistema


## Observações
- O sistema só faz uma busca geral (em todos os canais) na API do YouTube uma vez por dia, reutilizando os dados salvos nas execuções seguintes.
- São feitas buscas adicionais próximo dos horários agendados para as transmissões.
- Para forçar uma nova busca, basta pressionar **F** durante a execução ou apagar manualmente os arquivos em `pesquisa_api/`.

---
Desenvolvido para automação de monitoramento de transmissões ao vivo em múltiplos canais do YouTube via OBS Studio.
