class Constants:
    MSG_DELIMITER = "!"
    MSG_VALUE_DELIMITER = ":"

    mock_result = "sqt petr4T:PETR4:133540:1:20150810:2:9.87:3:9.87:4:9.88:5:133539:6:6:7:600:8:27340:9:32781100:10" \
                  ":322075778:11:10.03:12:9.57:13:9.69:14:9.81:15:133400:16:132300:17:26300:18:9700:19:900:20:3600:21" \
                  ":1.86:36:9.69:37:10.5:38:10.02:39:10.25:40:10.55:41:9.68:42:9.825:43:0:44:1:45:1:46:100:47" \
                  ":PETROBRAS:48:PN:49:1:50:20140403094008:51:20140403094008:52:0:53:0:54:20150810:56:0:57:200:58" \
                  ":000000:59:000000:60:40:61:232:62:40:63:308:64:00000000:65:6:66:5602042788:67:101:72:6:82:6:83:0" \
                  ":84:0:85:6:86:0.18:87:20150807:88:A:89:9.963:100:5602042788:101:0:102:0:103:0:104:0:105" \
                  ":BMFBR3806254:106:6-:107:10.8:108:8.82:109:18:119:2:111:100:112:0.01:113:100:114:560204279:115:0" \
                  ":116:BRL:117:PS:118:1004:119:0:120:000000:121:0:122:0:123:1:124:0:125:00000000000000:126:10:127:0" \
                  ":128:6:129:20150810:130:0!SYN "

    provider_msgs = {
        1: "Msg: Error 001 – Invalid command, Command: {0}.",
        2: "Msg: Error 002 – Instrument not found, Command: {0a}, Obj: {1}, Details: {2}.",
        3: "Msg: Error 003 – Access denied, Command: {0}, Obj: {1}, Details: {2}.",
        4: "Msg: Error 004 – Parameter invalid (null), Command: {0}.",
        5: "Msg: Error 005 – Parameter not found, Command: {0}.",
        6: "Msg: Error 006 – There are another running connection to the server.",
        7: "Msg: Error 007 – This client cannot send request anymore.",
        8: "Msg: Error 008 – Connection closed by server see:Error 006.)",
        9: "Msg: Error 009 – User access revoked by server.",
        10: "Msg: Error 010 – Parameter invalid.",
        11: "Msg: Error 011 – Server not found.",
        12: "Msg: Error 012 – Try reach the server at this new IP: {0}.",
        13: "Msg: Error 013 – SUID invalid",
        14: "Msg: Error 014 – SUID exceeds 14 characters",
        15: "Msg: Error 015 – Database Error.",
        16: "Msg: Error 016 – News Not Found.",
    }

    data_format = [
        {
            "description": "Cotações",
            "command": {
                "subscribe": [
                    {"cmd": "sqt", "symbol": ""},
                    {"cmd": "sqt", "symbol": "", "params": "N"}
                ],
                "unbscribe": {"cmd": "usq", "symbol": "", "params": "N {qtd|offset|ident}"}
            },
            "header": {"type": "T", "symbol": "", "time": "datetime.strptime('{0}', '%H%M%S').time()"},
            "payload": [
                {
                    "index": 1,
                    "desc": "Data da última modificação",
                    "name": "Data",
                    "type": "datetime.strptime('{0}', '%Y%m%d').date()",
                    "enabled": False
                },
                {
                    "index": 2,
                    "desc": "Preço do último negócio",
                    "name": "Ultimo",
                    "type": float,
                    "enabled": True
                },
                {
                    "index": 3,
                    "desc": "Melhor oferta de compra",
                    "name": "Compra",
                    "type": float,
                    "enabled": True
                },
                {
                    "index": 4,
                    "desc": "Melhor oferta de venda",
                    "name": "Venda",
                    "type": float,
                    "enabled": True
                },
                {
                    "index": 5,
                    "desc": "Horário do último negócio",
                    "name": "Hora Ult.",
                    "type": "datetime.strptime('{0}', '%H%M%S').time()",
                    "enabled": True
                },
                {
                    "index": 6,
                    "desc": "Quantidade do negócio atual",
                    "name": "Qtd. At.",
                    "type": int,
                    "enabled": True
                },
                {
                    "index": 7,
                    "desc": "Quantidade do último negócio",
                    "name": "Qtd. Ult.",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 8,
                    "desc": "Quantidade de negócios realizados",
                    "name": "Qtd. Negocios.",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 9,
                    "desc": "Volume acumulado dos negócios",
                    "name": "Volume",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 10,
                    "desc": "Volume financeiro dos negócios",
                    "name": "Vol. Fin.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 11,
                    "desc": "Maior preço do dia",
                    "name": "Maxima",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 12,
                    "desc": "Menor preço do dia",
                    "name": "Minima",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 13,
                    "desc": "Preço de fechamento do dia anterior",
                    "name": "Fech. Ant.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 14,
                    "desc": "Preço de abertura",
                    "name": "Abertura",
                    "type": float,
                    "enabled": True
                },
                {
                    "index": 15,
                    "desc": "Horário da melhor oferta de compra",
                    "name": "Hora Max.",
                    "type": "datetime.strptime('{0}', '%H%M%S').time()",
                    "enabled": False
                },
                {
                    "index": 16,
                    "desc": "Horário da melhor oferta de venda",
                    "name": "Hora Min.",
                    "type": "datetime.strptime('{0}', '%H%M%S').time()",
                    "enabled": False
                },
                {
                    "index": 17,
                    "desc": "Volume acumulado das melhores ofertas de compra",
                    "name": "Vol. Acum. Compra",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 18,
                    "desc": "Volume acumulado das melhores ofertas de venda",
                    "name": "Vol. Acum. Venda",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 19,
                    "desc": "Volume da melhor oferta de compra",
                    "name": "Vol. Melhor of. Compra",
                    "type": int,
                    "enabled": True
                },
                {
                    "index": 20,
                    "desc": "Volume da melhor oferta de venda",
                    "name": "Vol. Melhor of. Venda",
                    "type": int,
                    "enabled": True
                },
                {
                    "index": 21,
                    "desc": "Variação",
                    "name": "Variacao",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 36,
                    "desc": "Preço de fechamento da última semana",
                    "name": "Fech. Ult. Sem.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 37,
                    "desc": "Preço de fechamento do último Mês",
                    "name": "Fech. Ult. Mes.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 38,
                    "desc": "Preço de fechamento do último Ano",
                    "name": "Fech. Ult. Ano.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 39,
                    "desc": "Preço de abertura do dia anterior",
                    "name": "Abe. Ant.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 40,
                    "desc": "Maior preço do dia anterior",
                    "name": "Max. Ant.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 41,
                    "desc": "Menor preço do dia anterior",
                    "name": "Min. Ant.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 42,
                    "desc": "Média",
                    "name": "Media",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 43,
                    "desc": "VHDaily",
                    "name": "VHDaily",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 44,
                    "desc": "Código do Mercado",
                    "name": "Mercado",
                    "type": int,
                    "enabled": False,
                    "domain": {
                        1: "Bovespa",
                        2: "Dow Jones",
                        3: "BM&F",
                        4: "Índices",
                        5: "Money",
                        6: "Soma",
                        7: "Forex",
                        8: "Indicators",
                        9: "Others",
                        10: "Nyse",
                        11: "Bats",
                        12: "Nasdaq",
                        14: "BVL",
                        15: "SPIndexes",
                        16: "Liffe",
                        17: "Euronext Indices",
                        18: "CME",
                        19: "CME Mini"
                    }
                },
                {
                    "index": 45,
                    "desc": "Código do tipo do ativo",
                    "name": "Tp. Ativo",
                    "type": int,
                    "enabled": False,
                    "domain": {
                        1: "Ativo à vista",
                        2: "Opção",
                        3: "Índice",
                        4: "Commodity",
                        5: "Moeda",
                        6: "Termo",
                        7: "Futuro",
                        8: "Leilão",
                        9: "Bônus",
                        10: "Fracionário",
                        11: "Exercício de opção",
                        12: "Indicador",
                        13: "ETF",
                        15: "Volume",
                        16: "Opção sobre à vista",
                        17: "Opção sobre futuro",
                        18: "Ativo de teste"
                    }
                },
                {
                    "index": 46,
                    "desc": "Lote padrão",
                    "name": "Lote padrao",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 47,
                    "desc": "Descrição do ativo",
                    "name": "Descricao",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 48,
                    "desc": "Nome de classificação",
                    "name": "Nome de classificação",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 49,
                    "desc": "Forma de cotação",
                    "name": "Forma de cotação",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 50,
                    "desc": "Intraday Date (FORCES)",
                    "name": "Intraday Date (FORCES)",
                    "type": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "enabled": False
                },
                {
                    "index": 51,
                    "desc": "LastTrade Date (FORCES)",
                    "name": "LastTrade Date (FORCES)",
                    "type": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "enabled": False
                },
                {
                    "index": 52,
                    "desc": "Descrição abreviada do ativo",
                    "name": "Descricao abrev.",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 53,
                    "desc": "Identificador do negocio cancelado",
                    "name": "Ident. do negocio cancelado",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 54,
                    "desc": "Data do último negócio",
                    "name": "Data do último negócio",
                    "type": "datetime.strptime('{0}', '%Y%m%d').date()",
                    "enabled": False
                },
                {
                    "index": 56,
                    "desc": "Sentido das ofertas não atendidas ao preço de abertura",
                    "name": "Sent. Abe.",
                    "type": str,
                    "enabled": True,
                    "domain": {
                        "A": "COMPRA",
                        "V": "VENDA",
                        "0": "Não Informado"
                    }
                },
                {
                    "index": 57,
                    "desc": "Quantidade não atendida ao preço de abertura",
                    "name": "Quantidade não atendida ao preço de abertura",
                    "type": int,
                    "enabled": True
                },
                {
                    "index": 58,
                    "desc": "Horário programado para abertura do papel",
                    "name": "Horário programado para abertura do papel",
                    "type": "datetime.strptime('{0}', '%H%M%S').time()",
                    "enabled": True
                },
                {
                    "index": 59,
                    "desc": "Horário reprogramado para abertura do papel",
                    "name": "Horário reprogramado para abertura do papel",
                    "type": "datetime.strptime('{0}', '%H%M%S').time()",
                    "enabled": True
                },
                {
                    "index": 60,
                    "desc": "Código da corretora que fez a melhor oferta de compra",
                    "name": "Corretora Melhor Oferta",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 61,
                    "desc": "Código da corretora que fez a melhor oferta de venda",
                    "name": "Código da corretora que fez a melhor oferta de venda",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 62,
                    "desc": "Código da corretora que realizou a última compra",
                    "name": "Código da corretora que realizou a última compra",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 63,
                    "desc": "Código da corretora que realizou a última venda",
                    "name": "Código da corretora que realizou a última venda",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 64,
                    "desc": "Data do vencimento (Mercado de opções)",
                    "name": "Venc. Opcao",
                    "type": "datetime.strptime('{0}', '%Y%m%d').date()",
                    "enabled": False
                },
                {
                    "index": 65,
                    "desc": "Expirado",
                    "name": "Expirado",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 66,
                    "desc": "Número total de papéis",
                    "name": "Número total de papéis",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 67,
                    "desc": "Status do instrumento",
                    "name": "Status",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 72,
                    "desc": "Tipo da opção",
                    "name": "Tipo da opção",
                    "type": str,
                    "enabled": False,
                    "domain": {
                        "A": "Americana",
                        "E": "Européia",
                        "0": "Não existe"
                    }
                },
                {
                    "index": 74,
                    "desc": "Direção da opção",
                    "name": "Direção da opção",
                    "type": str,
                    "enabled": False,
                    "domain": {
                        "P": "Venda",
                        "C": "Compra"
                    }
                },
                {
                    "index": 81,
                    "desc": "Símbolo do ativo pai",
                    "name": "Símbolo do ativo pai",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 82,
                    "desc": "Preço teórico de abertura",
                    "name": "Preço teórico de abertura",
                    "type": float,
                    "enabled": True
                },
                {
                    "index": 83,
                    "desc": "Quantidade teórica",
                    "name": "Quantidade teórica",
                    "type": int,
                    "enabled": True
                },
                {
                    "index": 84,
                    "desc": "Status do ativo BOVESPA",
                    "name": "Status BOVESPA",
                    "type": int,
                    "enabled": True,
                    "domain": {
                        0: "Normal",
                        1: "Congelado",
                        2: "Suspenso",
                        3: "Leilão",
                        4: "Inibido",
                    }
                },
                {
                    "index": 85,
                    "desc": "Preço de Exercício BOVESPA",
                    "name": "Preço de Exercício BOVESPA",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 86,
                    "desc": "Diff (Preço Atual - Previous)",
                    "name": "Gap abertura",
                    "type": float,
                    "enabled": True
                },
                {
                    "index": 87,
                    "desc": "Data do Previous",
                    "name": "Data do Previous",
                    "type": "datetime.strptime('{0}', '%Y%m%d').date()",
                    "enabled": False
                },
                {
                    "index": 88,
                    "desc": "Fase do grupo do ativo",
                    "name": "Fase do grupo do ativo",
                    "type": str,
                    "enabled": True,
                    "domain": {
                        "P": "Pré abertura",
                        "A": "Abertura (sessão normal)",
                        "PN": "Pré fechamento",
                        "N": "Fechamento,",
                        "E": "Pré abertura do after",
                        "R": "Abertura do after",
                        "NE": "Fechamento do after",
                        "F": "Final"
                    }
                },
                {
                    "index": 89,
                    "desc": "Média do dia anterior BOVESPA",
                    "name": "Media",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 90,
                    "desc": "Intervalo de Margem (mercado BTC)",
                    "name": "Intervalo de Margem (mercado BTC)",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 94,
                    "desc": "Volume médio nos últimos 20 dias",
                    "name": "Volume médio nos últimos 20 dias",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 95,
                    "desc": "Market Capitalization",
                    "name": "Market Capitalizations",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 96,
                    "desc": "Tipo de Mercado",
                    "name": "Tipo de Mercado",
                    "type": str,
                    "enabled": False,
                    "domain": {
                        "RT": "RealTime",
                        "D": "Delay",
                        "EOD": "End of Day"
                    }
                },
                {
                    "index": 97,
                    "desc": "Variação do fechamento em uma semana",
                    "name": "Variação do fechamento em uma semana",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 98,
                    "desc": "Variação do fechamento em uma semana",
                    "name": "Variação do fechamento em uma semana",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 99,
                    "desc": "Variação do fechamento em um ano",
                    "name": "Variação do fechamento em um ano",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 100,
                    "desc": "Quantidade de contratos abertos",
                    "name": "Quantidade de contratos abertos",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 101,
                    "desc": "Número dias úteis até o vencimento",
                    "name": "Número dias úteis até o vencimento",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 102,
                    "desc": "Número dias para o vencimento",
                    "name": "Número dias para o vencimento",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 103,
                    "desc": "Ajuste do dia",
                    "name": "Ajuste",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 104,
                    "desc": "Ajuste do dia anterior",
                    "name": "Ajuste Ant.",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 105,
                    "desc": "SecurityId (BMF FIX)",
                    "name": "SecurityId (BMF FIX)",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 106,
                    "desc": "TickDirection(BMF FIX)",
                    "name": "TickDirection(BMF FIX)",
                    "type": str,
                    "enabled": False,
                    "domain": ['+', '-', '0+', '0-']
                },
                {
                    "index": 107,
                    "desc": "TunnelUpperLimit",
                    "name": "TunnelUpperLimit",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 108,
                    "desc": "TunnelLowerLimit",
                    "name": "TunnelLowerLimit",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 109,
                    "desc": "TradingPhase(BMF FIX)",
                    "name": "TradingPhase(BMF FIX)",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 110,
                    "desc": "TickSize",
                    "name": "TickSize",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 111,
                    "desc": "Volume mínimo de negociação do instrumento",
                    "name": "Volume mínimo de negociação do instrumento",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 112,
                    "desc": "Intervalo mínimo para incrementos de preço",
                    "name": "Intervalo mínimo para incrementos de preço",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 113,
                    "desc": "Quantidade mínima para o instrumento em uma oferta",
                    "name": "Quantidade mínima para o instrumento em uma oferta",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 114,
                    "desc": "Quantidade máxima para o instrumento em uma oferta",
                    "name": "Quantidade máxima para o instrumento em uma oferta",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 115,
                    "desc": "Número único de identificação do instrumento",
                    "name": "Número único de identificação do instrumento",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 116,
                    "desc": "Moeda utilizada no preço",
                    "name": "Moeda utilizada no preço",
                    "type": str,
                    "enabled": False,
                    "domain": ['BRL', 'EUR', 'USD']
                },
                {
                    "index": 117,
                    "desc": "SecurityType",
                    "name": "SecurityType",
                    "type": str,
                    "enabled": False,
                    "domain": ['FUT', 'OPT', 'SPOT', 'SOPT', 'FOPT', 'DTERM']
                },
                {
                    "index": 118,
                    "desc": "Código de negociação do instrumento",
                    "name": "Código de negociação do instrumento",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 119,
                    "desc": "Produto associado ao instrumento",
                    "name": "Produto associado ao instrumento",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 120,
                    "desc": "Mês e ano de vencimento",
                    "name": "Mês e ano de vencimento",
                    "type": "datetime.strptime('{0}', '%Y%m').date()",
                    "enabled": False
                },
                {
                    "index": 121,
                    "desc": "Preço de exercício da opção",
                    "name": "Preço de exercício da opção",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 122,
                    "desc": "Moeda do preço de exercício da opção",
                    "name": "Moeda do preço de exercício da opção",
                    "type": str,
                    "enabled": False,
                    "domain": ['BRL', 'EUR', 'USD']
                },
                {
                    "index": 123,
                    "desc": "Multiplicador do contrato",
                    "name": "Multiplicador do contrato",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 124,
                    "desc": "Código que representa o tipo de preço do instrumento",
                    "name": "Código que representa o tipo de preço do instrumento",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 125,
                    "desc": "Horário em que um instrumento não é mais passível de negociação",
                    "name": "Horário em que um instrumento não é mais passível de negociação",
                    "type": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "enabled": False
                },
                {
                    "index": 126,
                    "desc": "Indica o grupo ao qual o ativo pertence",
                    "name": "Indica o grupo ao qual o ativo pertence",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 127,
                    "desc": "Ajuste atual em taxa",
                    "name": "Ajuste atual em taxa",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 128,
                    "desc": "Ajuste anterior em taxa",
                    "name": "Ajuste anterior em taxa",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 129,
                    "desc": "Data do Ajuste atual em taxa",
                    "name": "Data do Ajuste atual em taxa",
                    "type": "datetime.strptime('{0}', '%Y%m%d').date()",
                    "enabled": False
                },
                {
                    "index": 130,
                    "desc": "Número de saques até data de vencimento",
                    "name": "Número de saques até data de vencimento",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 134,
                    "desc": "Variação do volume da hora com base na média do volume do horário nos últimos 20 dias",
                    "name": "Variação do volume da hora com base na média do volume do horário nos últimos 20 dias",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 135,
                    "desc": "Variação do volume até a hr. com base na méd. do volume até o horário nos últimos 20 dias",
                    "name": "Variação do volume até a hr. com base na méd. do volume até o horário nos últimos 20 dias",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 136,
                    "desc": "Código do setor do Ativo",
                    "name": "Código do setor do Ativo",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 137,
                    "desc": "Código do subsetor do Ativo",
                    "name": "Código do subsetor do Ativo",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 138,
                    "desc": "Código do segmento do Ativo",
                    "name": "Código do segmento do Ativo",
                    "type": int,
                    "enabled": False
                },
                {
                    "index": 139,
                    "desc": "settlement_type",
                    "name": "settlement_type",
                    "type": str,
                    "enabled": False
                },
                {
                    "index": 140,
                    "desc": "ref_price",
                    "name": "ref_price",
                    "type": float,
                    "enabled": False
                },
                {
                    "index": 141,
                    "desc": "ref_price_date",
                    "name": "ref_price_date",
                    "type": float,
                    "enabled": False
                }
            ]
        },
        {
            "description": "Book",
            "command": {
                "subscribe": [
                    {"cmd": "bqt", "symbol": ""}
                ],
                "unbscribe": {"cmd": "ubq", "symbol": ""}
            },
            "header": {"type": "B", "symbol": ""},
            "payload": [
                {
                    "index": "A",
                    "posicao": int,
                    "direcao": str,
                    "preco": float,
                    "quantidade": int,
                    "corretora": int,
                    "data_hora": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "orderid": str,
                    "tipo_oferta": str
                },
                {
                    "index": "U",
                    "posicao_nova": int,
                    "posicao_antiga": int,
                    "direcao": str,
                    "preco": float,
                    "quantidade": int,
                    "corretora": int,
                    "data_hora": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "orderid": str,
                    "tipo_oferta": str
                },
                {
                    "index": "E"
                },
                {
                    "index": "D",
                    "tipo": int,
                    "posicao": int,
                    "direcao": str
                }
            ]
        },
        {
            "description": "MiniBook",
            "command": {
                "subscribe": [
                    {"cmd": "mbq", "symbol": "", "params": "N"},
                    {"cmd": "mbq", "symbol": "", "params": "{qtd} N"}
                ],
                "unbscribe": {"cmd": "umb", "symbol": "", "params": "{qtd}"}
            },
            "header": {"type": "M", "symbol": ""},
            "payload": [
                {
                    "index": "A",
                    "posicao": int,
                    "direcao": str,
                    "preco": float,
                    "quantidade": int,
                    "corretora": int,
                    "data_hora": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "orderid": str,
                    "quantidade_ofertas": int,
                    "tipo_oferta": str
                },
                {
                    "index": "U",
                    "posicao_nova": int,
                    "posicao_antiga": int,
                    "direcao": str,
                    "preco": float,
                    "quantidade": int,
                    "corretora": int,
                    "data_hora": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "orderid": str,
                    "quantidade_ofertas": int,
                    "tipo_oferta": str
                },
                {
                    "index": "E",
                    "quantidade_ofertas": int,
                },
                {
                    "index": "D",
                    "tipo": int,
                    "direcao": str,
                    "posicao": int,
                    "quantidade_ofertas": int
                }
            ]
        },
        {
            "description": "TimesTrades",
            "command": {
                "subscribe": [
                    {"cmd": "gqt", "symbol": "", "params": "S {qtd|ident}"},
                    {"cmd": "gqt", "symbol": "", "params": "N {qtd|offset|ident}"}
                ],
                "unbscribe": {"cmd": "uqt", "symbol": ""}
            },
            "header": {"type": "GQT", "symbol": ""},
            "payload": [
                {
                    "index": "V",
                    "operacao": {"A": "Adição de negócio", "D": "Remoção de negócio",
                                 "R": "Remoção de  todos os negócios"},
                    "horario_negocio": "datetime.strptime('{0}', '%Y%m%d%H%M%S')",
                    "preco": float,
                    "corretora_comprou": int,
                    "corretora_vendeu": int,
                    "quantidade": int,
                    "identificador_negocio": int,
                    "identificador_requisicao": int,
                    "direto": {0: "Agressão", 1: "Cross Order"},
                    "agressor": {"I": "Indefinido", "A": "Comprador", "V": "Vendedor"}
                },
                {
                    "index": "E",
                    "identificador_requisicao": int
                }
            ]
        }
    ]
