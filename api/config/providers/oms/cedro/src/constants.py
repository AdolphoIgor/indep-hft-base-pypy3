class Constants:
    MSG_DELIMITER = "SYN"
    MSG_FIELD_DELIMITER = " "
    MSG_VALUE_DELIMITER = "="

    oms_format = {
        "msg": {
            "header": [
                {
                    "tag": 8,
                    "name": "BeginString",
                    "required": True,
                    "datatype": str,
                    "calculated": True,
                    "comments": "BeginString = “FIX.4.4”. Deve ser o primeiro campo da mensagem.",
                    "default": "FIX.4.4"
                },
                {
                    "tag": 9,
                    "name": "BodyLength",
                    "required": True,
                    "datatype": int,
                    "calculated": True,
                    "comments": "Quantidade de bytes do corpo da mensagem. Deve ser o segundo campo da mensagem."
                },
                {
                    "tag": 35,
                    "name": "MsgType",
                    "required": True,
                    "datatype": str,
                    "comments": "Identificador da mensagem. Deve ser o terceiro campo da mensagem."
                },
                {
                    "tag": 34,
                    "name": "MsgSeqNum",
                    "required": True,
                    "datatype": int,
                    "calculated": True,
                    "comments": "Número de seqüência da mensagem na sessão."
                },
                {
                    "tag": 43,
                    "name": "PossDupFlag",
                    "required": False,
                    "datatype": bool,
                    "comments": "Quando Y indica que essa é uma mensagem que tem possibilidade de ser duplicada ("
                                "no caso de reenvio para preencher buracos nos números de seqüência das "
                                "mensagens)."
                },
                {
                    "tag": 49,
                    "name": "SenderCompID",
                    "required": True,
                    "datatype": str,
                    "calculated": True,
                    "comments": "Identificador do sistema que envia a mensagem. Para mensagens enviadas pelo "
                                "Crystal Broker = 'CRYSTAL_BROKER'. Para mensagens recebidas pelo Crystal "
                                "Broker = identificador da contraparte que enviou a mensagem. Esse identificador "
                                "é igual ao login (Username) informado na mensagem de Logon (MsgType = A)."
                },
                {
                    "tag": 56,
                    "name": "TargetCompID",
                    "required": True,
                    "datatype": str,
                    "calculated": True,
                    "comments": "Identificador do sistema que vai receber a mensagem. Para mensagens enviadas "
                                "pelo Crystal Broker = identificador da contraparte que receberá a mensagem ("
                                "igual ao login - Username informado na mensagem de Logon - MsgType = A). Para "
                                "mensagens recebidas pelo Crystal Broker = 'CRYSTAL_BROKER'.",
                    "default": "CDRFIX"
                },
                {
                    "tag": 50,
                    "name": "SenderSubID",
                    "required": False,
                    "datatype": str,
                    "calculated": False,
                    "comments": "Identificador para o login interno da sessão. Utilizado nos casos em que a "
                                "sessão é utilizada por vários usuários."
                },
                {
                    "tag": 52,
                    "name": "SendingTime",
                    "required": True,
                    "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                    "calculated": True,
                    "comments": "Data e Hora de envio da mensagem."
                },
                {
                    "tag": 97,
                    "name": "PossResend",
                    "required": False,
                    "datatype": "bool",
                    "comments": "Quando Y indica que essa é uma mensagem resultante de requisição de reenvio."
                }
            ],
            "footer": [
                {
                    "tag": 93,
                    "name": "SignatureLength",
                    "required": True,
                    "datatype": int,
                    "calculated": True,
                    "comments": "Número de caracteres do campo Signature."
                },
                {
                    "tag": 89,
                    "name": "Signature",
                    "required": True,
                    "calculated": True,
                    "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                    "comments": "Token de sessão do usuário."
                },
                {
                    "tag": 10,
                    "name": "CheckSum",
                    "required": True,
                    "datatype": int,
                    "calculated": True,
                    "comments": "Contem o checksum do conteúdo da mensagem enviada ao provider."
                }
            ],
            "ident": [
                {
                    "tag": 55,
                    "name": "Symbol",
                    "required": True,
                    "datatype": str,
                    "comments": "Símbolo. O mercado exige que esse campo seja adequadamente preenchido. Ele "
                                "contém a forma inteligível do campo SecurityID, disponível na mensagem de lista "
                                "de instrumentos."
                },
                {
                    "tag": 48,
                    "name": "SecurityID",
                    "required": False,
                    "datatype": str,
                    "comments": "Identificador do instrumento, assim como definido pelo mercado."
                },
                {
                    "tag": 22,
                    "name": "SecurityIDSource",
                    "required": False,
                    "datatype": str,
                    "comments": "8 = Símbolo de Difusão.",
                    "default": 8
                },
                {
                    "tag": 207,
                    "name": "SecurityExchange",
                    "required": False,
                    "datatype": str,
                    "comments": "Mercado ao qual o instrumento pertence. “XBMF” = BM&F.",
                    "default": "XBSP"
                },
                {
                    "tag": 541,
                    "name": "MaturityDate",
                    "required": False,
                    "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                    "comments": "Indica a data de vencimento do instrumento/opção."
                },
                {
                    "tag": 10984,
                    "name": "Issuing",
                    "required": False,
                    "datatype": str,
                    "comments": ""
                },
                {
                    "tag": 10985,
                    "name": "ApplicationDays",
                    "required": False,
                    "datatype": int,
                    "comments": ""
                },
                {
                    "tag": 10986,
                    "name": "RewardDescription",
                    "required": False,
                    "datatype": str,
                    "comments": ""
                },
                {
                    "tag": 10987,
                    "name": "AvailableQuantity",
                    "required": False,
                    "datatype": int,
                    "comments": ""
                },
                {
                    "tag": 10988,
                    "name": "UnitPrice",
                    "required": False,
                    "datatype": float,
                    "comments": ""
                },
                {
                    "tag": 10989,
                    "name": "AvailablePrice",
                    "required": False,
                    "datatype": float,
                    "comments": ""
                },
                {
                    "tag": 10990,
                    "name": "MinimumApplicationPrice",
                    "required": False,
                    "datatype": float,
                    "comments": ""
                },
                {
                    "tag": 10993,
                    "name": "TradedRate",
                    "required": False,
                    "datatype": float,
                    "comments": ""
                },
                {
                    "tag": 10994,
                    "name": "TradedRateT",
                    "required": False,
                    "datatype": float,
                    "comments": ""
                },
                {
                    "tag": 10995,
                    "name": "IssuanceDate",
                    "required": False,
                    "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                    "comments": ""
                },
                {
                    "tag": 10996,
                    "name": "LiquidityDate",
                    "required": False,
                    "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                    "comments": ""
                },
                {
                    "tag": 10997,
                    "name": "SecurityIndex",
                    "required": False,
                    "datatype": str,
                    "comments": ""
                },
                {
                    "tag": 10998,
                    "name": "PercentIndex",
                    "required": False,
                    "datatype": float,
                    "comments": ""
                },
                {
                    "tag": 10999,
                    "name": "IssuanceRate",
                    "required": False,
                    "datatype": float,
                    "comments": ""
                }
            ]
        },
        "MsgTypes": [
            {
                "MsgType": "0",
                "type": "Heartbeat",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 112,
                        "name": "TestReqID",
                        "required": False,
                        "datatype": str,
                        "comments": "Obrigatório quando o heartbeat é resultado de uma mensagem de Test Request ("
                                    "MsgType = 1)."
                    }
                ]
            },
            {
                "MsgType": "A",
                "type": "Logon",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 98,
                        "name": "EncryptMethod",
                        "required": True,
                        "datatype": int,
                        "comments": "Deve ser “0”.",
                        "default": 0
                    },
                    {
                        "tag": 108,
                        "name": "HeartBtInt",
                        "required": True,
                        "datatype": int,
                        "comments": "Recomendado: “30” (segundos).",
                        "default": 30
                    },
                    {
                        "tag": 141,
                        "name": "ResetSeqNumFlag",
                        "required": False,
                        "datatype": str,
                        "comments": ""
                    },
                    {
                        "tag": 789,
                        "name": "NextExpectedMsgSeqNum",
                        "required": False,
                        "datatype": int,
                        "comments": ""
                    },
                    {
                        "tag": 464,
                        "name": "TestMessageIndicator",
                        "required": False,
                        "datatype": bool,
                        "comments": "Enviado apenas pelo Crystal Broker. Indica se essa sessão Fix é uma sessão "
                                    "de teste ou produção. Útil para prevenir acidentes. Valores Válidos: Y = Sim "
                                    "(Ambiente de Teste) N = Não (Ambiente de Produção).",
                        "domain": ["Y", "N"]
                    },
                    {
                        "tag": 553,
                        "name": "Username",
                        "required": True,
                        "datatype": str,
                        "comments": "Login do cliente no sistema. Não há problemas em enviar esse dado na "
                                    "mensagem, uma vez que há criptografia no nível de camada de rede (SSL)."
                                    "Enviado apenas pelo iniciador."
                    },
                    {
                        "tag": 554,
                        "name": "Password",
                        "required": True,
                        "datatype": str,
                        "comments": "Senha do cliente no sistema. Não há problemas em enviar esse dado na "
                                    "mensagem, uma vez que há criptografia no nível de camada de rede (SSL)."
                                    "Enviado apenas pelo iniciador."
                    },
                    {
                        "tag": 925,
                        "name": "NewPassword",
                        "required": False,
                        "datatype": str,
                        "comments": "Nova senha para mudança de uma senha antiga expirada."
                    },
                    {
                        "tag": 20110,
                        "name": "UserType",
                        "required": False,
                        "datatype": str,
                        "comments": "Tipo de autenticação a ser usada. V=Administrador (via banco) U=Usuário (via "
                                    "RTP).",
                        "domain": ["V", "U"]
                    },
                    {
                        "tag": 10060,
                        "name": "ClientDocument",
                        "required": False,
                        "datatype": str,
                        "comments": "Número do documento do cliente para a recuperação da senha."
                    },
                    {
                        "tag": 95,
                        "name": "RawDataLength",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de caracteres do campo RawData."
                    },
                    {
                        "tag": 96,
                        "name": "RawData",
                        "required": False,
                        "datatype": str,
                        "comments": "Caracteres que correspondem aos dados resultantes do processo de logon."
                                    "Enviado apenas pelo roteador. Este campo contém três informações, "
                                    "separadas pelo caractere Line-Feed (Valor ASCII = 10), listados abaixo: 1 – "
                                    "Login a ser usado para conectar no subsistema de difusão; 2 – Senha a ser "
                                    "usada para conectar no subsistema de difusão; 3 – Token de sessão, "
                                    "que deve ser enviado em todas as mensagens enviadas pelo iniciador, "
                                    "no Rodapé Padrão; Os três dados estão no seguinte formato: "
                                    "Login<09> Senha<09> Token."
                    },
                    {
                        "tag": 10673,
                        "name": "DaysUntilPasswordExpiration",
                        "required": False,
                        "datatype": int,
                        "comments": "Dias restantes até a expiração da senha do usuáio."
                    },
                    {
                        "tag": 9933,
                        "name": "ApplicationName",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Dias restantes até a expiração da senha do usuáio."
                    },
                    {
                        "tag": 10733,
                        "name": "ApplicationVersion",
                        "required": False,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Tag que informa a versão da aplicação utilizada pelo usuário(sessão)."
                    }
                ]
            },
            {
                "MsgType": "1",
                "type": "Test Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 112,
                        "name": "TestReqID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador que deve ser retornado no heartbeat de resposta."
                    },
                    {
                        "tag": 20109,
                        "name": "Locale",
                        "required": False,
                        "datatype": str,
                        "comments": "Código do Idioma. Ex: pt-BR Se o valor não for informado o OMS irá utilizar "
                                    "o valor atribuído na configuração."
                    }
                ]
            },
            {
                "MsgType": "2",
                "type": "Resend Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 7,
                        "name": "BeginSeqNum",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de seqüência da primeira mensagem do intervalo a ser reenviado."
                    },
                    {
                        "tag": 16,
                        "name": "EndSeqNum",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de seqüência da última mensagem do intervalo a ser reenviado. Se a "
                                    "requisição for de apenas uma mensagem, então BeginSeqNum = EndSeqNum Se a "
                                    "requisição for de todas as mensagens a partir de um determinado número, "
                                    "então EndSeqNum = “0”."
                    }
                ]
            },
            {
                "MsgType": "3",
                "type": "Reject",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 45,
                        "name": "RefSeqNum",
                        "required": True,
                        "datatype": int,
                        "comments": "MsgSeqNum da mensagem rejeitada."
                    },
                    {
                        "tag": 371,
                        "name": "RefTagID",
                        "required": False,
                        "datatype": int,
                        "comments": "Número do campo (Tag) referenciado na mensagem FIX rejeitada."
                    },
                    {
                        "tag": 372,
                        "name": "RefMsgType",
                        "required": False,
                        "datatype": str,
                        "comments": "MsgType da mensagem FIX rejeitada."
                    },
                    {
                        "tag": 373,
                        "name": "SessionRejectionReason",
                        "required": True,
                        "datatype": int,
                        "comments": "Código que identifica o motivo de rejeição da mensagem a nível de sessão: 0 "
                                    "= Número de campo inválido 1 = Falta de campo obrigatório 2 = Campo não "
                                    "definido para este tipo de mensagem 3 = Campo indefinido 4 = Campo sem valor "
                                    "5 = Valor está incorreto (fora do intervalo) para este campo 6 = Formato de "
                                    "dado incorreto para valor 7 = Problema de decriptografia 8 = Problema de "
                                    "Assinatura 9 = Problema de CompID 10 = Problema na validação de SendingTime "
                                    "11 = MsgType inválido 13 = Campo aparece mais de uma vez 14 = Campo "
                                    "especificado fora da ordem requerida 15 = Campo de Repeating group fora da "
                                    "ordem 16 = Contador NumInGroup incorreto para Repeating Group 17 = Valor de "
                                    "campo “dado” sem delimitador (caractere SOH) 99 = Outro ",
                        "domain": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 99]
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Quando for possível, mensagem explicando o motivo de rejeição.",
                        "domain": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 99]
                    }
                ]
            },
            {
                "MsgType": "4",
                "type": "Sequence Reset",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 123,
                        "name": "GapFillFlag",
                        "required": False,
                        "datatype": bool,
                        "comments": "Y = modo Gap Fill N = modo Reset."
                    },
                    {
                        "tag": 36,
                        "name": "NewSeqNo",
                        "required": True,
                        "datatype": int,
                        "comments": "Novo número de seqüência."
                    }
                ]
            },
            {
                "MsgType": "5",
                "type": "Logout",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Explicação do motivo do Logout (se houver)."
                    },
                    {
                        "tag": 20118,
                        "name": "LogonRejCode",
                        "required": False,
                        "datatype": int,
                        "comments": "Codigo do motivo do logout 0 = WRONG_PASSWORD 1 = WRONG_USERNAME 2 = "
                                    "BLOCKED_USER 3 = EXPIRED_PASSWORD 4 = SESSION_IN_USE 5 = "
                                    "APPLICATION_NOT_FOUND 6 = PERMISSION_DENIED 7 = PASSWORD_NOT_EXPIRED 8 = "
                                    "NEW_PASSWORD_FAILED ",
                        "domain": [0, 1, 2, 3, 4, 5, 6, 7, 8]
                    }
                ]
            },
            {
                "MsgType": "U0",
                "type": "Server Available Hosts",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 10011,
                        "name": "NoBrokerHosts",
                        "required": True,
                        "datatype": int,
                        "comments": "Quantidade de Hosts de Crystais Broker,em ordem decrescente de número de "
                                    "usuário.",
                        "subtags": [
                            {
                                "tag": 10012,
                                "name": "BrokerHost",
                                "required": True,
                                "datatype": str,
                                "comments": "Host para conexão no Crystal Broker."
                            }
                        ]
                    }
                ]
            },
            {
                "MsgType": "B",
                "type": "News",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 10000,
                        "name": "NewsID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único da notícia, como definido pelo Crystal."
                    },
                    {
                        "tag": 10009,
                        "name": "NewsRequestID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da requisição de notícia, como definido pelo iniciador, "
                                    "caso essa mensagem seja resultado de um News Request (MsgType = U3)."
                    },
                    {
                        "tag": 42,
                        "name": "OrigTime",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "comments": "Data e hora da criação da notícia."
                    },
                    {
                        "tag": 61,
                        "name": "Urgency",
                        "required": False,
                        "datatype": str,
                        "comments": "Indica a urgência da mensagem. Pode ter um dos seguintes valores: 0 = Normal "
                                    "1 = Flash – Notícia de prioridade alta, que de preferência deve disparar "
                                    "algum tipo de sinal mais claro ao usuário indicando seu recebimento 2 = "
                                    "Background – Notícia de prioridade baixa."
                    },
                    {
                        "tag": 146,
                        "name": "NoRelatedSyn",
                        "required": False,
                        "datatype": int,
                        "comments": "Cabeçalho da notícia."
                    },
                    {
                        "tag": 33,
                        "name": "LinesOfText",
                        "required": True,
                        "datatype": str,
                        "comments": "Indica a quantidade de linhas do texto.",
                        "subtags": [
                            {
                                "tag": 58,
                                "name": "Text",
                                "required": True,
                                "datatype": str,
                                "comments": "Texto da linha atual."
                            }
                        ]
                    },
                    {
                        "tag": 149,
                        "name": "URLLink",
                        "required": False,
                        "datatype": str,
                        "comments": "URL com um link para informação adicional."
                    },
                    {
                        "tag": 10001,
                        "name": "NewsRejectReason",
                        "required": False,
                        "datatype": int,
                        "comments": "Motivo da rejeição, caso essa mensagem seja resposta de uma requisição "
                                    "NewsRequest (MsgType = U3) 0 = NewsID inválido 1 = NewsRequestID inválido 2 "
                                    "= Usuário sem permissão para notícia 3 = Outro (Descrição no campo Text – 58)"
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": True,
                        "datatype": str,
                        "comments": "Texto descrevendo o motivo da rejeição, caso seja necessário."
                    }
                ]
            },
            {
                "MsgType": "U1",
                "type": "News Headlines Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 10002,
                        "name": "NewsHeadlinesID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único da requisição de Headlines, como definido pelo iniciador."
                    },
                    {
                        "tag": 10004,
                        "name": "InitialDate",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "comments": "Data inicial da busca. Caso não seja informado, serão retornadas todas as "
                                    "mensagens. Caso seja informado, deve ser repetido a cada requisição de uma "
                                    "nova página."
                    },
                    {
                        "tag": 10005,
                        "name": "FinalDate",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "comments": "Data final da busca. Caso seja omitido e o Initial Date esteja definido, "
                                    "então a busca retornará as mensagens de InitialDate até o dia corrente. Caso "
                                    "InitialDate não esteja definido, FinalDate será desprezado, "
                                    "e serão retornadas todas as mensagens dos últimos 30 dias. A diferença entre "
                                    "InitialDate e FinalDate não pode ser maior que 30 dias corridos, resultando "
                                    "em rejeição da requisição."
                    }
                ]
            },
            {
                "MsgType": "U2",
                "type": "News Headlines Report",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 10002,
                        "name": "NewsHeadlinesID",
                        "required": True,
                        "datatype": str,
                        "comments": "Eco do identificador único na sessão da requisição de Headlines."
                    },
                    {
                        "tag": 893,
                        "name": "LastFragment",
                        "required": False,
                        "datatype": bool,
                        "comments": "Indica se este é o último fragmento da requisição ou não. Caso seja omitido, "
                                    "o valor default é N. Valores possíveis: Y = Última mensagem N = Não é a "
                                    "última mensagem.",
                        "domain": ["N", "Y"],
                        "default": "N"
                    },
                    {
                        "tag": 10008,
                        "name": "TotNoNews",
                        "required": True,
                        "datatype": int,
                        "comments": "Quantidade total de notícias a serem retornadas."
                    },
                    {
                        "tag": 10010,
                        "name": "NoNewsHeadlines",
                        "required": True,
                        "datatype": str,
                        "comments": "Número de títulos (Headlines) de notícias na página atual.",
                        "subtags": [
                            {
                                "tag": 10000,
                                "name": "NewsID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador único da notícia."
                            },
                            {
                                "tag": 148,
                                "name": "Headline",
                                "required": True,
                                "datatype": str,
                                "comments": "Cabeçalho da notícia."
                            },
                            {
                                "tag": 42,
                                "name": "OrigTime",
                                "required": False,
                                "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                                "comments": "Data e hora da criação da notícia."
                            },
                            {
                                "tag": 61,
                                "name": "Urgency",
                                "required": False,
                                "datatype": str,
                                "comments": "Indica a prioridade da mensagem. Pode ter um dos seguintes valores: "
                                            "0 = Normal."
                            }
                        ]
                    },
                    {
                        "tag": 10003,
                        "name": "NewsHeadlinesRejectReason",
                        "required": False,
                        "datatype": int,
                        "comments": "Indica a prioridade da mensagem. Pode ter um dos seguintes valores: 0 = Normal"
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Texto descrevendo o motivo da rejeição, caso seja necessário."
                    }
                ]
            },
            {
                "MsgType": "U3",
                "type": "News Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 10009,
                        "name": "NewsRequestID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único na sessão da requisição de notícia, como definido pelo "
                                    "iniciador."
                    },
                    {
                        "tag": 10000,
                        "name": "NewsID",
                        "required": False,
                        "datatype": bool,
                        "comments": "Identificador da notícia que se deseja requisitar, como definido pelo "
                                    "roteador."
                    }
                ]
            },
            {
                "MsgType": "D",
                "type": "New OrderSingle",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 11,
                        "name": "ClOrdID",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Identificador da ordem. Deve ser único por dia ou sessão, e definido pelo "
                                    "iniciador."
                    },
                    {
                        "tag": 583,
                        "name": "ClOrdLinkID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da ordem à qual essa ordem está associada e possui dependência "
                                    "(só será enviada ao mercado caso a ordem dependente seja totalmente "
                                    "executada."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": True,
                        "datatype": str,
                        "comments": "Direção da ordem. Valores válidos: 1 = Compra 2 = Venda",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 38,
                        "name": "OrderQty",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de contratos a serem executados."
                    },
                    {
                        "tag": 110,
                        "name": "MinQty",
                        "required": False,
                        "datatype": int,
                        "comments": "Menor quantidade de contratos que deve ser executada."
                    },
                    {
                        "tag": 111,
                        "name": "MaxFloor",
                        "required": False,
                        "datatype": int,
                        "comments": "Número máximo de contratos da ordem a serem mostrados no livro de ofertas a "
                                    "cada momento."
                    },
                    {
                        "tag": 40,
                        "name": "OrdType",
                        "required": True,
                        "datatype": str,
                        "comments": "Tipo da ordem. Pode ter um dos seguintes valores:  2 = Limite 4 = Stop Limit "
                                    "K = Market with leftover as Limit S = Start",
                        "domain": ["2", "4", "K", "S"]
                    },
                    {
                        "tag": 529,
                        "name": "OrderRestrictions",
                        "required": False,
                        "datatype": str,
                        "comments": "Restrições relacionadas à ordem. Se mais de uma restrição se aplicar à "
                                    "ordem, esse campo poderá conter instruções múltiplas separadas por espaço."
                                    "Valores: 1 = Program trading 7 = Entidade estrangeira 8 = Participante de "
                                    "mercado estrangeiro",
                        "domain": [1, 7, 8]
                    },
                    {
                        "tag": 99,
                        "name": "StopPx",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de Stop para uma ordem Stop Limit ou Start. Obrigatório apenas quando "
                                    "OrdType = 4 ou S.",
                        "domain": ['4', 'S']
                    },
                    {
                        "tag": 44,
                        "name": "Price",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço sugerido por contrato."
                    },
                    {
                        "tag": 10306,
                        "name": "StopGainPx",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de StopGain para uma ordem Stop Limit. Possível apenas em OrdType = 4 "
                                    "ou S, mas não obrigatório.",
                        "domain": ['4', 'S']
                    },
                    {
                        "tag": 640,
                        "name": "Price2",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço limite para Stop Gain."
                    },
                    {
                        "tag": 10432,
                        "name": "MovingStart",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de ínicio móvel, configurado para Ordens Start/Stop Móvel. Obrigatório "
                                    "quando Initial Change é informado."
                    },
                    {
                        "tag": 10431,
                        "name": "InitialChangeType",
                        "required": False,
                        "datatype": int,
                        "comments": "Código que determina se valor em campo InitialChange será representação "
                                    "percentual ou absoluta. Valores possíveis: 1 = Percentual 2 = Absoluto "
                                    "Obrigatório quando InitialChange é informado.",
                        "domain": ['1', '2']
                    },
                    {
                        "tag": 10430,
                        "name": "InitialChange",
                        "required": False,
                        "datatype": int,
                        "comments": "Preço de alteração inicial do Price, quando LastTrade ultrapassar "
                                    "MovingStart, configurado quando ordem Start/Stop Móvel. Obrigatório quando "
                                    "campos MovingStart e InitialChangeType forem informados. (Se percentual, "
                                    "1.0 = 100%)"
                    },
                    {
                        "tag": 30078,
                        "name": "PricePercentage",
                        "required": False,
                        "datatype": float,
                        "comments": "Percentual usado para calcular o preço limite em uma ordem Start/Stop Móvel.",
                        "domain": ['1', '2']
                    },
                    {
                        "tag": 59,
                        "name": "TimeInForce",
                        "required": False,
                        "datatype": str,
                        "comments": "Especifica o tipo de duração da ordem. A ausência desse campo indica que seu "
                                    "valor é 0 (Dia). Pode ter um dos seguintes valores: 0 = Dia (ou sessão) 1 = "
                                    "Good Till Cancel (GTC) 3 = Executa (mesmo que parcial) imediatamente ou "
                                    "Cancela (IOC) 4 = Executa por completo ou Cancela (FOK) 6 = Good Till Date ("
                                    "GTD) 7 = At The Close (ATC) A = Good For Auction (GFA).",
                        "domain": ['0', '1', '3', '4', '6', '7', 'A'],
                        "default": 0
                    },
                    {
                        "tag": 10121,
                        "name": "BrokerID",
                        "required": False,
                        "datatype": str,
                        "comments": "Código da corretora de destino.",
                        "domain": ['0', '1', '3', '4', '6', '7', 'A']
                    },
                    {
                        "tag": 78,
                        "name": "NoAllocs",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de contas para alocação pré-negociação. Deve ser sempre 1, sendo que a "
                                    "alocação é permitida para apenas um cliente.",
                        "default": 1,
                        "subtags": [
                            {
                                "tag": 79,
                                "name": "AllocAccount",
                                "required": True,
                                "datatype": str,
                                "comments": "Código da conta."
                            },
                            {
                                "tag": 661,
                                "name": "AllocAcctIDSource",
                                "required": True,
                                "datatype": int,
                                "comments": "Fonte da conta. Valor aceito: 99 – Outro (custom or proprietary code)",
                                "default": 99
                            }
                        ]
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating Group para informar os códigos dos participantes da oferta. Deve "
                                    "conter combinações únicas de PartyID, PartyIDSource e PartyRole.",
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "calculated": True,
                                "comments": "Identificador do Participante.",
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: D = "
                                            "Propietary/Custom code.",
                                "default": 'D'
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 12 = Executing "
                                            "Trader 36 = Entering Trader 40 = Transfer to Firm",
                                "default": 36
                            }
                        ]
                    },
                    {
                        "tag": 60,
                        "name": "TransactTime",
                        "required": True,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "calculated": True,
                        "comments": "Data e hora da criação da ordem."
                    },
                    {
                        "tag": 77,
                        "name": "PositionEffect",
                        "required": False,
                        "datatype": str,
                        "comments": "Indica se a posição resultante de uma operação deve ser de fechamento. Valor "
                                    "aceito: C = fechamento ",
                        "domain": ["C"]
                    },
                    {
                        "tag": 826,
                        "name": "TradeAllocIndicator",
                        "required": False,
                        "datatype": int,
                        "comments": "Identifica como a operação deve ser especificada. Valor aceito: 1 = "
                                    "especificação obrigatória (operação de repasse); informações sobre "
                                    "especificação não-fornecidas (incompletas) A ausência desse campo indica que "
                                    "a especificação não é obrigatória ou foi fornecida com a operação.",
                        "domain": ["1"]
                    },
                    {
                        "tag": 10122,
                        "name": "OrderStrategy",
                        "required": False,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Nome da estratégia."
                    },
                    {
                        "tag": 21,
                        "name": "HandlInst",
                        "required": False,
                        "datatype": str,
                        "comments": "Indica que é uma ordem administrada. Valor aceito: 2 = Ordem automática com "
                                    "possível intervenção do broker 3 = Manual.",
                        "domain": ["2", "3"]
                    },
                    {
                        "tag": 10264,
                        "name": "OrderTag",
                        "required": False,
                        "datatype": str,
                        "lenght": 50,
                        "comments": "Tag (observação) informada para a ordem. Para ordens enviadas ao mercado "
                                    "através de uma sessão EntryPoint seu valor é repassado para o campo Memo("
                                    "5149). Obs.: No EntryPoint são permitidos no máximo 50 caracteres para este "
                                    "campo."
                    },
                    {
                        "tag": 847,
                        "name": "TargetStrategy",
                        "required": False,
                        "datatype": int,
                        "comments": "A estratégia de destino da ordem."
                    },
                    {
                        "tag": 848,
                        "name": "TargetStrategyParameters",
                        "required": False,
                        "datatype": str,
                        "comments": "Parametros da estratégia de destino definida entre as partes."
                    },
                    {
                        "tag": 10719,
                        "name": "SourceAddress",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Utilizado para armazenar a origem da ordem."
                    },
                    {
                        "tag": 10870,
                        "name": "IsStopToMarket",
                        "required": False,
                        "datatype": str,
                        "comments": "Opção de envio de Stop Loss para o mercado."
                    },
                    {
                        "tag": 10964,
                        "name": "FullFilled",
                        "required": False,
                        "datatype": bool,
                        "comments": "Define se a estratégia OSO será disparada somente com a ordem totalmente "
                                    "executada."
                    },
                    {
                        "tag": 555,
                        "name": "NoLegs",
                        "required": False,
                        "datatype": int,
                        "comments": "Informa a quantidade de pernas na estratégia. Usado em estratégias One Send "
                                    "Other.",
                        "subtags": [
                            {
                                "tag": 40,
                                "name": "OrdType",
                                "required": False,
                                "datatype": str,
                                "comments": "Tipo da ordem a ser disparada. Tipos possíveis: 2 = Limite 4 = Stop "
                                            "Limite ",
                                "domain": [2, 4]
                            },
                            {
                                "tag": 59,
                                "name": "TimeInForce",
                                "required": False,
                                "datatype": str,
                                "comments": "Tipos de vencimentos a serem enviado.",
                                "domain": [2, 4]
                            },
                            {
                                "tag": 836,
                                "name": "PegOffsetType",
                                "required": False,
                                "datatype": int,
                                "comments": "Tipo dos valores para a estratégia. Valores possíveis: 0 = Price 2 = "
                                            "Ticks.",
                                "domain": [0, 2]
                            },
                            {
                                "tag": 516,
                                "name": "OrderPercent",
                                "required": False,
                                "datatype": float,
                                "comments": "Percentual da perna irá consumir da ordem executada."
                            },
                            {
                                "tag": 44,
                                "name": "Price",
                                "required": False,
                                "datatype": float,
                                "comments": "Preço somado ao valor da execução para o preço de perda enviado na "
                                            "estratégia."
                            },
                            {
                                "tag": 99,
                                "name": "StopPx",
                                "required": False,
                                "datatype": float,
                                "comments": "Tick ou Preço somado ao valor da execução para o preço de disparo de "
                                            "perda enviado na estrategia."
                            },
                            {
                                "tag": 640,
                                "name": "Price2",
                                "required": False,
                                "datatype": float,
                                "comments": "Preço somado ao valor da execução para o preço de ganho enviado na "
                                            "estratégia."
                            },
                            {
                                "tag": 10306,
                                "name": "StopGainPx",
                                "required": False,
                                "datatype": float,
                                "comments": "Tick ou Preço somado ao valor da execução para o preço de disparo de "
                                            "ganho enviado na estratégia."
                            },
                            {
                                "tag": 211,
                                "name": "PegOffsetValue",
                                "required": False,
                                "datatype": float,
                                "comments": "Tick somado ao valor da execução para o preço de perda/ganho enviado "
                                            "na estratégia."
                            }
                        ]
                    }
                ]
            },
            {
                "MsgType": "s",
                "type": "New Order Cross",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 548,
                        "name": "CrossID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da ordem Cross. Deve ser único por dia ou sessão, e definido "
                                    "pelo iniciador."
                    },
                    {
                        "tag": 549,
                        "name": "CrossType",
                        "required": True,
                        "datatype": int,
                        "comments": "Tipo da ordem Cross. Valor aceito: 1 = Negociação Cross que ou é "
                                    "completamente executada ou não. Equivalente a tudo ou nada.",
                        "domain": ["", "1"]
                    },
                    {
                        "tag": 550,
                        "name": "CrossPriorization",
                        "required": True,
                        "datatype": int,
                        "comments": "Indica se um lado ou outro da ordem deve ser priorizado. Valor aceito: 0 = "
                                    "Nenhum",
                        "domain": ["", "0"]
                    },
                    {
                        "tag": 40,
                        "name": "OrdType",
                        "required": True,
                        "datatype": str,
                        "comments": "Tipo da ordem. Valor aceito: 2 = Limite.",
                        "domain": ["", "2"]
                    },
                    {
                        "tag": 44,
                        "name": "Price",
                        "required": True,
                        "datatype": float,
                        "comments": "Preço por contrato.",
                        "domain": ["", "2"]
                    },
                    {
                        "tag": 60,
                        "name": "TransactTime",
                        "required": True,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "calculated": True,
                        "comments": "Data/Hora da criação da ordem."
                    },
                    {
                        "tag": 10121,
                        "name": "BrokerID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da corretora para a qual a ordem será enviada."
                    },
                    {
                        "tag": 552,
                        "name": "NoSides",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da corretora para a qual a ordem será enviada.",
                        "subtags": [
                            {
                                "tag": 54,
                                "name": "Side",
                                "required": True,
                                "datatype": str,
                                "comments": "Lado da Ordem. Os valores válidos são: 1 = Compra 2 = Venda.",
                                "domain": [1, 2]
                            },
                            {
                                "tag": 11,
                                "name": "ClOrdID",
                                "required": True,
                                "datatype": str,
                                "calculated": True,
                                "comments": "Identificador único da ordem que será gerada por esse lado da ordem "
                                            "Cross. Deve ser único por dia ou sessão, e definido pelo iniciador.",
                                "domain": [1, 2]
                            },
                            {
                                "tag": 38,
                                "name": "OrderQty",
                                "required": True,
                                "datatype": int,
                                "comments": "Número de contratos a serem executados."
                            },
                            {
                                "tag": 77,
                                "name": "PositionEffect",
                                "required": False,
                                "datatype": int,
                                "comments": "Indica se a posição resultante de uma operação deve ser de "
                                            "fechamento. Valor aceito: C = fechamento.",
                                "domain": ["C"]
                            },
                            {
                                "tag": 78,
                                "name": "NoAllocs",
                                "required": False,
                                "datatype": int,
                                "comments": "Número de contas para alocação prénegociação. Se presente deve ser "
                                            "sempre 1, sendo que a alocação é permitida para apenas um cliente.",
                                "domain": ["1"],
                                "subtags": [
                                    {
                                        "tag": 79,
                                        "name": "AllocAccount",
                                        "required": False,
                                        "datatype": str,
                                        "comments": "Código da conta. Obrigatório caso o NoAllocs > 0."
                                    },
                                    {
                                        "tag": 661,
                                        "name": "AllocAcctIDSource",
                                        "required": False,
                                        "datatype": int,
                                        "comments": "Fonte da conta. Valor aceito: 99 =Outro (custom or "
                                                    "proprietary code)",
                                        "default": 99
                                    }
                                ]
                            },
                            {
                                "tag": 453,
                                "name": "NoPartyID",
                                "required": True,
                                "datatype": int,
                                "comments": "Repeating Group para informar os códigos dos participantes da "
                                            "oferta. Deve conter combinações únicas de PartyID, PartyIDSource e "
                                            "PartyRole",
                                "subtags": [
                                    {
                                        "tag": 448,
                                        "name": "PartyID",
                                        "required": True,
                                        "datatype": str,
                                        "comments": "Identificador do Participante."
                                    },
                                    {
                                        "tag": 447,
                                        "name": "PartyIDSource",
                                        "required": True,
                                        "datatype": str,
                                        "comments": "Identifica a origem do PartyID. O único valor aceito é: D = "
                                                    "Propietary/Custom code.",
                                        "domain": ["D"],
                                    },
                                    {
                                        "tag": 452,
                                        "name": "PartyRole",
                                        "required": True,
                                        "datatype": int,
                                        "comments": "Identifica o tipo do participante. Valores aceitos: 12 = "
                                                    "Executing Trader 36 = Entering Trader 40 = Transfer to Firm",
                                        "domain": [12, 36, 40],
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "tag": 826,
                        "name": "TradeAllocIndicator",
                        "required": False,
                        "datatype": int,
                        "comments": "Identifica como a operação deve ser especificada. Valor aceito: 1 = "
                                    "especificação obrigatória (operação de repasse); informações sobre "
                                    "especificação não-fornecidas (incompletas) A ausência desse campo indica que "
                                    "a especificação não é obrigatória ou foi fornecida com a operação."
                    },
                    {
                        "tag": 10264,
                        "name": "OrderTag",
                        "required": False,
                        "datatype": str,
                        "comments": "Tag (observação) informada para a ordem. Para ordens enviadas ao mercado "
                                    "através de uma sessão EntryPoint seu valor é repassado para o campo Memo("
                                    "5149). Obs.: No EntryPoint são permitidos no máximo 50 caracteres para este "
                                    "campo."
                    },
                ]
            },
            {
                "MsgType": "8",
                "type": "Execution Report",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 37,
                        "name": "OrderID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da ordem como definido pelo roteador."
                    },
                    {
                        "tag": 11,
                        "name": "ClOrdID",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Identificador da ordem como definido pelo iniciador."
                    },
                    {
                        "tag": 41,
                        "name": "OrigCIOrdID",
                        "required": False,
                        "datatype": str,
                        "comments": "Contém o ClOrdID da ordem editada.Condicionalmente requerido quando ExecType "
                                    "possuir um dos seguintes valores: 4 = Canceled (Cancelamento) 5 = Replaced ("
                                    "Edição) 6 = Pending Cancel (Cancelamento Pendente) E = Pending Replace ("
                                    "Edição ainda não confirmada pelo mercado).",
                        "domain": ['4', '5', '6', "E"]
                    },
                    {
                        "tag": 790,
                        "name": "OrdStatusReqID",
                        "required": False,
                        "datatype": str,
                        "comments": "Caso a mensagem seja resultado de um Order Status Request (MsgType = H), "
                                    "esse campo conterá o OrdStatusReqID da mensagem que originou esse Execution "
                                    "Report."
                    },
                    {
                        "tag": 198,
                        "name": "SecondaryOrderID",
                        "required": False,
                        "datatype": str,
                        "comments": "Especifica o OrderID secundário da ordem. Se uma or-dem é recebida com "
                                    "MaxFloor > 0, toda vez que a quantidade total executada é adicionada de "
                                    "MaxFloor, um novo SecondaryOrderID é atribuído à ordem, e é por esse "
                                    "SecondaryOrderID que a ordem será identifi-cada no livro de ofertas. O "
                                    "SecondaryOrderID também é alterado nas confirmações de edição e cancelamento."
                    },
                    {
                        "tag": 548,
                        "name": "CrossID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da ordem Cross,como definido pelo iniciador."
                    },
                    {
                        "tag": 17,
                        "name": "ExecID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único da mensagem de execução definido pelo roteador."
                    },
                    {
                        "tag": 584,
                        "name": "MassStatusReqID",
                        "required": False,
                        "datatype": str,
                        "comments": "Requerido se respondendo a uma mensagem do tipo Order Mass Status Request."
                                    "Identificador único da mensagem de requisição de ordens, como definido pelo "
                                    "iniciador."
                    },
                    {
                        "tag": 911,
                        "name": "TotNumReports",
                        "required": False,
                        "datatype": int,
                        "comments": "Identifica o número de mensagens de Execution Reportque são retornadas como "
                                    "resposta de um Order Mass Status Request. Se apenas uma mensagem Execution "
                                    "Report é enviada, este campo é opcional."
                    },
                    {
                        "tag": 912,
                        "name": "LastRptRequested",
                        "required": False,
                        "datatype": bool,
                        "comments": "Indica que esta é a última mensagem de Execution Report que será retornada "
                                    "como resposta de um Order Mass Status Request. Valores possíveis: Y = Último "
                                    "Execution Report retornado N = Caso contrário."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 150,
                        "name": "ExecType",
                        "required": True,
                        "datatype": str,
                        "comments": "Descreve a ação que disparou essa mensagem de Execution Report – veja "
                                    "OrdStatus (39) para verificar o status atual da ordem. Valores possíveis: 0 "
                                    "=New (Nova) 4 =Canceled (Cancelamento) 5 =Replaced (Edição) 6 =Pending "
                                    "Cancel (Cancelamento Pendente, resultado de Order Cancel Request(MsgType = "
                                    "F) e que ainda não recebeu confirmação do mercado) 8 =Rejected (Rejeição) A "
                                    "=Pending New (Pendente – resultado de envio de nova ordem com mercado ainda "
                                    "fechado para negociação) C =Expired (Expiração) D = Restated(Reconfirmação) "
                                    "E =Pending Replace (Edição ainda não confirmada pelo mercado) F =Trade ("
                                    "Negócio) I =Order Status (Status de Ordem – Resultado de uma mensagem de "
                                    "Order Mass Status Request(MsgType=AF)) R = Received L = Triggered ",
                        "domain": ['0', '4', '5', '6', '8', 'A', 'C', 'D', 'E', 'F', 'I', 'R', 'L']
                    },
                    {
                        "tag": 39,
                        "name": "OrdStatus",
                        "required": True,
                        "datatype": str,
                        "comments": "Status atual da ordem. Valores possíveis: 0 = New (Recebida) 1 = Partially "
                                    "Filled (Parcialmente Executada) 2 = Filled (Completamente Executada) 4 = "
                                    "Canceled (Cancelada) 5 = Replaced (Editada) 6 = Pending Cancel (Cancelamento "
                                    "Pendente) 8 = Rejected (Rejeitada) A = Pending New (Pendente - esperando "
                                    "abertura do mercado para ser enviada) C = Expired (Expirada) E = Pending "
                                    "Replace (Esperando Edição) R = Received",
                        "domain": ['0', '1', '2', '4', '5', '6', '8', 'A', 'C', 'E', 'R']
                    },
                    {
                        "tag": 40,
                        "name": "OrdType",
                        "required": False,
                        "datatype": str,
                        "comments": "Tipo da ordem. Condicionalmente requerido quando ExecType for diferente de 8 "
                                    "(Rejeitada). Pode ter um dos seguintes valores: 2 = Limite 4 = Stop Limit K "
                                    "= Market with leftover as Limit S = Start",
                        "domain": ['2', '4', 'K', 'S']
                    },
                    {
                        "tag": 378,
                        "name": "ExecRestatementReason",
                        "required": False,
                        "datatype": int,
                        "comments": "Indica motivo de reafirmação, se disponível. Valor emitida pela "
                                    "BM&FBOVESPA:: 4 – Broker option",
                        "domain": ['', '4']
                    },
                    {
                        "tag": 103,
                        "name": "OrdRejReason",
                        "required": False,
                        "datatype": int,
                        "comments": "Código que identifica o motivo de rejeição da ordem. Condicionalmente "
                                    "requerida se ExecType = 8. Valores possíveis: 0 = Opção do servidor 1 = "
                                    "Símbolo Desconhecido 2 = Pregão fechado 3 = Ordem excedeu limite 4 = Tarde "
                                    "demais para entrar 5 = Ordem desconhecida 6 = Ordem duplicada (e.g. ClOrdID "
                                    "duplicado) 11 = Característica da ordem não suportada 13 = Quantidade "
                                    "incorreta 15 = Conta desconhecida 99 = Outro (erro genérico, ver campo Text "
                                    "para mais informações)",
                        "domain": ['0', '1', '2', '3', '4', '5', '6', '11', '13', '15', '99']
                    },
                    {
                        "tag": 10100,
                        "name": "OrdRejSource",
                        "required": False,
                        "datatype": int,
                        "comments": "Local em que a mensagem esta sendo rejeitada. Obrigatório quando ExecType = "
                                    "8. Valores possíveis:, 1 = BM&F 2 = Crystal Broker (OMS) 4 = "
                                    "ManagedOrderAdmin.",
                        "domain": ['1', '2', '4']
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": True,
                        "datatype": int,
                        "comments": "Direção da ordem. Valores possíveis: 1 = Compra 2 = Venda",
                        "domain": ['1', '2']
                    },
                    {
                        "tag": 38,
                        "name": "OrderQty",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de contratos ordenados."
                    },
                    {
                        "tag": 44,
                        "name": "Price",
                        "required": True,
                        "datatype": float,
                        "comments": "Preço por contrato. Requerido se especificado na ordem."
                    },
                    {
                        "tag": 99,
                        "name": "StopPx",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de Stop em uma ordem do tipo Stop Limit(OrdType = 4)."
                    },
                    {
                        "tag": 10306,
                        "name": "StopGainPx",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de StopGain para uma ordem Stop Limit. Possível apenas em OrdType = 4 "
                                    "ou S, mas não obrigatório."
                    },
                    {
                        "tag": 640,
                        "name": "Price2",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço limite para Stop Gain."
                    },
                    {
                        "tag": 10432,
                        "name": "MovingStart",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de ínicio móvel, configurado para Ordens Start/Stop Móvel. Obrigatório "
                                    "quando InitialChange é informado."
                    },
                    {
                        "tag": 10431,
                        "name": "InitialChangeType",
                        "required": False,
                        "datatype": int,
                        "comments": "Código que determina se valor em campo InitialChange será representação "
                                    "percentual ou absoluta. Valores possíveis: 1 = Percentual 2 = Absoluto "
                                    "Obrigatório quando InitialChange é informado.",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 10430,
                        "name": "InitialChange",
                        "required": False,
                        "datatype": int,
                        "comments": "Preço de alteração inicial do Price, quando LastTrade ultrapassar "
                                    "MovingStart, configurado quando ordem Start/Stop Móvel. Obrigatório quando "
                                    "campos MovingStart e InitialChangeType forem informados. (Se percentual, "
                                    "1.0 = 100%)."
                    },
                    {
                        "tag": 10449,
                        "name": "CurrentPrice",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço limite atual, quando houver configuração Start/Stop Móvel."
                    },
                    {
                        "tag": 10450,
                        "name": "CurrentStopPx",
                        "required": False,
                        "datatype": float,
                        "comments": "StopPx atual, quando houver configuração Start/Stop Móvel."
                    },
                    {
                        "tag": 30078,
                        "name": "PricePercentage",
                        "required": False,
                        "datatype": float,
                        "comments": "Percentual usado para calcular o preço limite em uma ordem Start/Stop Móvel."
                    },
                    {
                        "tag": 10455,
                        "name": "StartStopClOrdId",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da ordem Start/Stop que originou esta ordem."
                    },
                    {
                        "tag": 6,
                        "name": "AvgPx",
                        "required": True,
                        "datatype": float,
                        "comments": "Preço médio dos contratos já negociados até agora na ordem."
                    },
                    {
                        "tag": 32,
                        "name": "LastQty",
                        "required": False,
                        "datatype": int,
                        "comments": "Quantidade de contratos comprados/vendidos nesse último negócio."
                                    "Condicionalmente requerido quando ExecType = F (Trade)."
                    },
                    {
                        "tag": 31,
                        "name": "LastPx",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço desse último negócio. Condicionalmente requerido quando ExecType = F ("
                                    "Trade)."
                    },
                    {
                        "tag": 110,
                        "name": "MinQty",
                        "required": False,
                        "datatype": int,
                        "comments": "Quantidade mínima que deve ser executada em um negócio. Cópia do valor de "
                                    "MinQty da mensagem que originou a ordem."
                    },
                    {
                        "tag": 111,
                        "name": "MaxFloor",
                        "required": False,
                        "datatype": int,
                        "comments": "Número máximo de contratos da ordem a serem mostrados no livro de ofertas a "
                                    "cada momento . Cópia do valor de MaxFloor da mensagem que originou a ordem."
                    },
                    {
                        "tag": 151,
                        "name": "LeavesQty",
                        "required": True,
                        "datatype": int,
                        "comments": "Quantidade de contratos ainda abertos para execução. LeavesQty = OrderQty – "
                                    "CumQty."
                    },
                    {
                        "tag": 14,
                        "name": "CumQty",
                        "required": True,
                        "datatype": int,
                        "comments": "Quantidade de contratos já executados."
                    },
                    {
                        "tag": 30032,
                        "name": "RestatedCumQty",
                        "required": False,
                        "datatype": int,
                        "comments": ""
                    },
                    {
                        "tag": 59,
                        "name": "TimeInForce",
                        "required": False,
                        "datatype": str,
                        "comments": "Especifica o tipo de duração da ordem. A ausência desse campo indica que seu "
                                    "valor é 0 (Dia). Pode ter um dos seguintes valores: 0 = Dia (ou sessão) 1 = "
                                    "Good Till Cancel (GTC) 3 = Executa (mesmo que parcial) imediatamente ou "
                                    "Cancela (IOC) 4 = Executa por completo ou Cancela (FOK) 6 = Good Till Date ("
                                    "GTD) 7 = At The Close (ATC) A = Good For Auction (GFA).",
                        "domain": ['0', '1', '2', '3', '4', '6', '7', 'A'],
                        "default": 0
                    },
                    {
                        "tag": 126,
                        "name": "ExpireTime",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "comments": "Data e hora da expiração da ordem, este campo dever ser definido em UTC. "
                                    "Obrigatório quando TimeInForce = GTD (6) "
                    },
                    {
                        "tag": 75,
                        "name": "TradeDate",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d').time()",
                        "comments": "Indica a data da negociação indicada nessa mensagem, no formato YYYYMMDD. A "
                                    "ausência desse campo indica o dia corrente."
                    },
                    {
                        "tag": 6032,
                        "name": "UniqueTradeId",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador único desse negócio. Condicionalmente requerido se ExecType = F."
                    },
                    {
                        "tag": 1,
                        "name": "Account",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da conta."
                    },
                    {
                        "tag": 79,
                        "name": "AllocAccount",
                        "required": False,
                        "datatype": str,
                        "comments": "Conta de destino para a qual a ordem foi enviada."
                    },
                    {
                        "tag": 10121,
                        "name": "BrokerID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da corretora para a qual a ordem foi enviada."
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating Group para informar os códigos dos participantes da oferta. Deve "
                                    "conter combinações únicas de PartyID, PartyIDSource e PartyRole.",
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do Participante."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: D = "
                                            "Propietary/Custom code "
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 12 = Executing "
                                            "Trader 29 = Intermediary 36 = Entering Trader 40 = Transfer to Firm ",
                                "domain": [12, 29, 36, 40]
                            },
                        ]
                    },
                    {
                        "tag": 382,
                        "name": "NoContraBrokers",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de contra partes envolvidas no negócio. Condicionalmente requerido "
                                    "quando reportar um negócio.",
                        "subtags": [
                            {
                                "tag": 375,
                                "name": "ContraBroker",
                                "required": False,
                                "datatype": str,
                                "comments": "Identifica a contra parte. Obrigatório caso o NoContraBrokers > 0."
                            },
                            {
                                "tag": 337,
                                "name": "ContraTrader",
                                "required": False,
                                "datatype": str,
                                "comments": "Identifica o trader da contra parte."
                            }
                        ]
                    },
                    {
                        "tag": 60,
                        "name": "TransactTime",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "calculated": True,
                        "comments": "Hora da execução ou da criação da ordem."
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Texto de formato livre."
                    },
                    {
                        "tag": 21,
                        "name": "HandlInst",
                        "required": False,
                        "datatype": str,
                        "comments": "Indica que é uma ordem administrada. Valor aceito: 2 = Ordem automática com "
                                    "possível intervenção do broker 3 = Manual.",
                        "domain": ['2, 3']
                    },
                    {
                        "tag": 826,
                        "name": "TradeAllocIndicator",
                        "required": False,
                        "datatype": int,
                        "comments": "Identifica como a operação deve ser especificada. Valor aceito: 1 = "
                                    "especificação obrigatória (operação de repasse); informações sobre "
                                    "especificação não-fornecidas (incompletas). A ausência desse campo indica "
                                    "que a especificação não é obrigatória ou foi fornecida com a operação ."
                    },
                    {
                        "tag": 10122,
                        "name": "OrderStrategy",
                        "required": False,
                        "datatype": str,
                        "comments": "Nome da estratégia."
                    },
                    {
                        "tag": 10264,
                        "name": "OrderTag",
                        "required": False,
                        "datatype": str,
                        "length": 50,
                        "comments": "Tag (observação) informada para a ordem. Para ordens enviadas ao mercado "
                                    "através de uma sessão EntryPoint seu valor é repassado para o campo Memo("
                                    "5149). Obs.: No EntryPoint são permitidos no máximo 50 caracteres para este "
                                    "campo."
                    },
                    {
                        "tag": 10130,
                        "name": "PortID",
                        "required": False,
                        "datatype": str,
                        "comments": "Código da porta de destino."
                    },
                    {
                        "tag": 9933,
                        "name": "ApplicationName",
                        "required": True,
                        "datatype": str,
                        "comments": "Tag que informa o identificador da aplicação utilizada pelo usuário(sessão)."
                    },
                    {
                        "tag": 847,
                        "name": "TargetStrategy",
                        "required": False,
                        "datatype": int,
                        "comments": "A estratégia de destino da ordem."
                    },
                    {
                        "tag": 848,
                        "name": "TargetStrategyParameters",
                        "required": False,
                        "datatype": str,
                        "comments": "Parametros da estratégia de destino definida entre as partes."
                    },
                    {
                        "tag": 636,
                        "name": "WorkingIndicator",
                        "required": False,
                        "datatype": bool,
                        "comments": "Indica se a ordem está ativa."
                    },
                    {
                        "tag": 10719,
                        "name": "SourceAddress",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Utilizado para armazenar a origem da ordem."
                    },
                    {
                        "tag": 10870,
                        "name": "IsStopToMarket",
                        "required": False,
                        "datatype": str,
                        "comments": "Opção de envio de Stop Loss para o mercado."
                    },
                ]
            },
            {
                "MsgType": "G",
                "type": "Order Cancel / Replace Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 41,
                        "name": "OrigClOrdID",
                        "required": True,
                        "datatype": str,
                        "comments": "ClOrdID da ordem que o cliente está tentando editar."
                    },
                    {
                        "tag": 37,
                        "name": "OrderID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da ordem como definido pelo roteador. Se esse campo estiver "
                                    "presente, o valor de OrigClOrdID é ignorado."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 11,
                        "name": "ClOrdID",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Identificador único da ordem de edição. Deve ser único por dia ou sessão e "
                                    "definido pelo iniciador."
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": True,
                        "datatype": str,
                        "comments": "Direção da ordem. Valores válidos: 1 = Compra 2 = Venda ",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 38,
                        "name": "OrderQty",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de contratos a serem ordenados.",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 111,
                        "name": "MaxFloor",
                        "required": False,
                        "datatype": int,
                        "comments": "Número máximo de contratos da ordem a serem mostrados no livro de ofertas a "
                                    "cada momento."
                    },
                    {
                        "tag": 40,
                        "name": "OrdType",
                        "required": True,
                        "datatype": str,
                        "comments": "Tipo da ordem. Pode ter um dos seguintes valores: 2 = Limite 4 = Stop Limit "
                                    "K = Market with leftover as Limit S = Start ",
                        "domain": ['2', '4', 'K', 'S']
                    },
                    {
                        "tag": 529,
                        "name": "OrderRestrictions",
                        "required": False,
                        "datatype": str,
                        "comments": "Restrições relacionadas à ordem. Se mais de uma restrição se aplicar à "
                                    "ordem, esse campo poderá conter instruções múltiplas separadas por espaço."
                                    "Valores: 1 = Program trading 7 = Entidade estrangeira 8 = Participante de "
                                    "mercado estrangeiro ",
                        "domain": [1, 7, 8]
                    },
                    {
                        "tag": 44,
                        "name": "Price",
                        "required": True,
                        "datatype": float,
                        "comments": "Preço sugerido por contrato. Não obrigatório apenas quando OrdType = K"
                    },
                    {
                        "tag": 99,
                        "name": "StopPx",
                        "required": True,
                        "datatype": float,
                        "comments": "Preço de Stop para uma ordem Stop Limit. Possível apenas quando OrdType = 4 "
                                    "ou S.",
                        "domain": ['4', 'S']
                    },
                    {
                        "tag": 10306,
                        "name": "StopGainPx",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de StopGain para uma ordem Stop Limit. Possível apenas em OrdType = 4 "
                                    "ou S.",
                        "domain": ['4', 'S']
                    },
                    {
                        "tag": 640,
                        "name": "Price2",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço limite para Stop Gain."
                    },
                    {
                        "tag": 10432,
                        "name": "MovingStart",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de ínicio móvel, configurado para Ordens. Start/Stop Móvel."
                    },
                    {
                        "tag": 10431,
                        "name": "InitialChangeType",
                        "required": False,
                        "datatype": int,
                        "comments": "Código que determina se valor em campo InitialChange será representação "
                                    "percentual ou absoluta. Valores possíveis: 1 = Percentual 2 = Absoluto.",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 10430,
                        "name": "InitialChange",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço de alteração inicial do Price, quando LastTrade ultrapassar "
                                    "MovingStart, configurado quando ordem Start/Stop Móvel. (Se percentual, "
                                    "1.0 = 100%)."
                    },
                    {
                        "tag": 30078,
                        "name": "PricePercentage",
                        "required": False,
                        "datatype": float,
                        "comments": "Percentual usado para calcular o preço limite em uma ordem Start/Stop Móvel."
                    },
                    {
                        "tag": 78,
                        "name": "NoAllocs",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de contas para alocação prénegociação. Se presente deve ser sempre 1, "
                                    "sendo que a alocação é permitida para apenas um cliente.",
                        "subtags": [
                            {
                                "tag": 79,
                                "name": "AllocAccount",
                                "required": False,
                                "datatype": str,
                                "comments": "Código da conta. Esse valor não pode ser alterado caso o operador "
                                            "seja DMA."
                            },
                            {
                                "tag": 661,
                                "name": "AllocAcctIDSource",
                                "required": False,
                                "datatype": int,
                                "comments": "Fonte da conta. Valor aceito: 99 = Outro (custom or proprietary "
                                            "code)."
                            }
                        ]
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating Group para informar os códigos dos participantes da oferta. Deve "
                                    "conter combinações únicas de PartyID, PartyIDSource e PartyRole.",
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do Participante."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: D = "
                                            "Propietary/Custom code."
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 12 = Executing "
                                            "Trader 36 = Entering Trader 40 = Transfer to Firm ",
                                "domain": [12, 36, 40]
                            }
                        ]
                    },
                    {
                        "tag": 21,
                        "name": "HandlInst",
                        "required": False,
                        "datatype": str,
                        "comments": "Indica que é uma ordem administrada. Valor aceito: 2 = Ordem automática com "
                                    "possível intervenção do broker 3 = Manual",
                        "domain": [2, 3]
                    },
                    {
                        "tag": 60,
                        "name": "TransactTime",
                        "required": True,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "calculated": True,
                        "comments": "Data e hora da criação da ordem de edição."
                    },
                    {
                        "tag": 10264,
                        "name": "OrderTag",
                        "required": False,
                        "datatype": str,
                        "lenght": 50,
                        "comments": "Tag (observação) informada para a ordem. Para ordens enviadas ao mercado "
                                    "através de uma sessão EntryPoint seu valor é repassado para o campo Memo("
                                    "5149). Obs.: No EntryPoint são permitidos no máximo 50 caracteres para este "
                                    "campo."
                    },
                    {
                        "tag": 847,
                        "name": "TargetStrategy",
                        "required": False,
                        "datatype": int,
                        "comments": "A estratégia de destino da ordem."
                    },
                    {
                        "tag": 848,
                        "name": "TargetStrategyParameters",
                        "required": False,
                        "datatype": str,
                        "comments": "Parametros da estratégia de destino definida entre as partes."
                    },
                    {
                        "tag": 10719,
                        "name": "SourceAddress",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Utilizado para armazenar a origem da ordem."
                    }
                ]
            },
            {
                "MsgType": "F",
                "type": "Order Cancel Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 41,
                        "name": "OrigClOrdID",
                        "required": True,
                        "datatype": str,
                        "comments": "ClOrdID da ordem que o cliente está tentando editar."
                    },
                    {
                        "tag": 37,
                        "name": "OrderID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da ordem como definido pelo Crystal Broker. Se esse campo "
                                    "estiver presente, o valor de OrigClOrdID é ignorado."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 11,
                        "name": "ClOrdID",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Identificador único da ordem de cancelamento. Deve ser único por dia ou "
                                    "sessão e definido pelo iniciador."
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": True,
                        "datatype": str,
                        "comments": "Direção da ordem. Valores válidos: 1 = Compra 2 = Venda ",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 529,
                        "name": "OrderRestrictions",
                        "required": False,
                        "datatype": str,
                        "comments": "Restrições relacionadas à ordem. Se mais de uma restrição se aplicar à "
                                    "ordem, esse campo poderá conter instruções múltiplas separadas por espaço."
                                    "Valores: 1 = Program trading 7 = Entidade estrangeira 8 = Participante de "
                                    "mercado estrangeiro ",
                        "domain": [1, 7, 8]
                    },
                    {
                        "tag": 38,
                        "name": "OrderQty",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de contratos a serem ordenados.",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating Group para informar os códigos dos participantes da oferta. Deve "
                                    "conter combinações únicas de PartyID, PartyIDSource e PartyRole.",
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do Participante."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: D = "
                                            "Propietary/Custom code."
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 12 = Executing "
                                            "Trader 36 = Entering Trader 40 = Transfer to Firm ",
                                "domain": [12, 36, 40]
                            }
                        ]
                    },
                    {
                        "tag": 21,
                        "name": "HandlInst",
                        "required": False,
                        "datatype": str,
                        "comments": "Indica que é uma ordem administrada. Valor aceito: 2 = Ordem automática com "
                                    "possível intervenção do broker 3 = Manual",
                        "domain": [2, 3]
                    },
                    {
                        "tag": 60,
                        "name": "TransactTime",
                        "required": True,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "calculated": True,
                        "comments": "Data e hora da criação da ordem de cancelamento."
                    },
                    {
                        "tag": 10264,
                        "name": "OrderTag",
                        "required": False,
                        "datatype": str,
                        "lenght": 50,
                        "comments": "Tag (observação) informada para a ordem. Para ordens enviadas ao mercado "
                                    "através de uma sessão EntryPoint seu valor é repassado para o campo Memo("
                                    "5149). Obs.: No EntryPoint são permitidos no máximo 50 caracteres para este "
                                    "campo."
                    },
                    {
                        "tag": 847,
                        "name": "TargetStrategy",
                        "required": False,
                        "datatype": int,
                        "comments": "A estratégia de destino da ordem."
                    },
                    {
                        "tag": 848,
                        "name": "TargetStrategyParameters",
                        "required": False,
                        "datatype": str,
                        "comments": "Parametros da estratégia de destino definida entre as partes."
                    }
                ]
            },
            {
                "MsgType": "9",
                "type": "Order Cancel Reject",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 37,
                        "name": "OrderID",
                        "required": False,
                        "datatype": str,
                        "comments": "Se CxlRejReason = 1, então o valor desse campo é “NONE”. Senão, "
                                    "é o identificador da ordem como definido pelo Crystal Broker."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 11,
                        "name": "ClOrdID",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "Identificador único da mensagem que foi rejeitada definida pelo iniciador."
                    },
                    {
                        "tag": 41,
                        "name": "OrigClOrdID",
                        "required": True,
                        "datatype": str,
                        "comments": "ClOrdID da ordem que não pôde ser rejeitada."
                    },
                    {
                        "tag": 39,
                        "name": "OrdStatus",
                        "required": True,
                        "datatype": str,
                        "comments": "OrdStatus da ordem depois da rejeição do cancelamento. Se CxlRejReason = 1, "
                                    "o valor desse campo será 8 (Rejeitada). Valores possíveis: 0 = New ("
                                    "Recebida) 1 = Partially Filled (Parcialmente Executada) 2 = Filled ("
                                    "Completamente Executada) 4 = Canceled (Cancelada) 5 = Replaced (Editada) 6 = "
                                    "Pending Cancel (Cancelamento Pendente) 8 = Rejected (Rejeitada) A = Pending "
                                    "New (Pendente - esperando abertura do mercado para ser enviada) C = Expired "
                                    "(Expirada) E = Pending Replace (Esperando Edição).",
                        "domain": ['0', '1', '2', '4', '5', '6', '8', 'A', 'C', 'E']
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": False,
                        "datatype": str,
                        "comments": "Direção da ordem. Valores válidos: 1 = Compra 2 = Venda ",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 434,
                        "name": "CxlRejResponseTo",
                        "required": True,
                        "datatype": str,
                        "comments": "Identifica o tipo de requisição que gerou essa mensagem de rejeição. Valores "
                                    "aceitos: 1 =Order Cancel Request 2 =Order Cancel/Replace Request ",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 102,
                        "name": "CxlRejReason",
                        "required": False,
                        "datatype": int,
                        "comments": "Código que identifica o motivo de rejeição. Os valores válidos são: 0 = "
                                    "Muito tarde para ser cancelada 1 = Ordem desconhecida 99 = Outro ",
                        "domain": [0, 1, 99]
                    },
                    {
                        "tag": 10101,
                        "name": "CxlRejSource",
                        "required": False,
                        "datatype": int,
                        "comments": "Local em que a mensagem esta sendo rejeitada. Valores possíveis: 1 = BM&F 2 "
                                    "= Crystal Broker (OMS) 4 = ManagedOrderAdmin ",
                        "domain": [1, 2, 4]
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Descrição do erro no caso de CxlRejReason = 99 (Outro)."
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating Group para informar os códigos dos participantes da oferta. Deve "
                                    "conter combinações únicas de PartyID, PartyIDSource e PartyRole.",
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do Participante."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: D = "
                                            "Propietary/Custom code."
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 12 = Executing "
                                            "Trader 36 = Entering Trader 40 = Transfer to Firm ",
                                "domain": [12, 36, 40]
                            }
                        ]
                    },
                    {
                        "tag": 21,
                        "name": "HandlInst",
                        "required": False,
                        "datatype": str,
                        "comments": "Indica que é uma ordem administrada. Valor aceito: 2 = Ordem automática com "
                                    "possível intervenção do broker 3 = Manual",
                        "domain": [2, 3]
                    },
                    {
                        "tag": 10264,
                        "name": "OrderTag",
                        "required": False,
                        "datatype": str,
                        "lenght": 50,
                        "comments": "Tag (observação) informada para a ordem. Para ordens enviadas ao mercado "
                                    "através de uma sessão EntryPoint seu valor é repassado para o campo Memo("
                                    "5149). Obs.: No EntryPoint são permitidos no máximo 50 caracteres para este "
                                    "campo."
                    },
                    {
                        "tag": 848,
                        "name": "WorkingIndicator",
                        "required": False,
                        "datatype": bool,
                        "comments": "Indica se a ordem está ativa."
                    }
                ]
            },
            {
                "MsgType": "H",
                "type": "Order Status Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 11,
                        "name": "ClOrdID",
                        "required": True,
                        "datatype": str,
                        "calculated": True,
                        "comments": "ClOrdID da ordem que se deseja recuperar o status."
                    },
                    {
                        "tag": 790,
                        "name": "OrdStatusReqID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identifica unicamente esse Order Status Request na sessão. É enviado de "
                                    "volta no Execution Report de resposta. Deve ser único por dia ou sessão e "
                                    "definido pelo iniciador."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": False,
                        "datatype": str,
                        "comments": "Direção da ordem. Valores válidos: 1 = Compra 2 = Venda ",
                        "domain": [1, 2]
                    }
                ]
            },
            {
                "MsgType": "AF",
                "type": "Order Mass Status Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 584,
                        "name": "MassStatusReqID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único dessa requisição assinalado pela parte que envia o "
                                    "comando. Será usado nas mensagens de Excution Report para identificar que a "
                                    "mensagem foi gerada como resposta dessa requisição. Deve ser único por dia "
                                    "ou sessão e definido pelo iniciador."
                    },
                    {
                        "tag": 585,
                        "name": "MassStatusRequestType",
                        "required": True,
                        "datatype": int,
                        "comments": "Especifica o escopo da requisição. Valores aceitos: 8= Status de ordens para "
                                    "um PartyID.",
                        "domain": [8]
                    },
                    {
                        "tag": 10034,
                        "name": "OrdStatusReqType",
                        "required": False,
                        "datatype": str,
                        "comments": "Especifica se será retornado um histórico de todos os Execution Reports da "
                                    "sessão corrente, ou apenas o último status de cada ordem. Valores aceitos: 1 "
                                    "= Retorna o historio completo 2 = Retorna apenas o último status. Na "
                                    "ausência desse campo será considerado o valor 2.",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 37,
                        "name": "OrderID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador único da ordem.Este será usado apenas quando usuário quiser "
                                    "todos os status de apenas uma ordem, sendo a tag OrdStatusReqType igual a 1."
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating Group para informar os códigos dos participantes da oferta. Deve "
                                    "conter combinações únicas de PartyID, PartyIDSource e PartyRole.",
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do Participante."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: D = "
                                            "Propietary/Custom code."
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 12 = Executing "
                                            "Trader 36 = Entering Trader 40 = Transfer to Firm ",
                                "domain": [12, 36, 40]
                            }
                        ]
                    },
                    {
                        "tag": 55,
                        "name": "Symbol",
                        "required": False,
                        "datatype": str,
                        "comments": "Símbolo. A BM&FBOVESPA exige que esse campo seja adequadamente preenchido."
                                    "Ele contém a forma inteligível do campo SecurityID, disponível na mensagem "
                                    "de lista de instrumentos."
                    },
                    {
                        "tag": 78,
                        "name": "NoAllocs",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de contas. Indica os números das contas de clientes para as quais "
                                    "devem ser buscadas as ordens, no caso de ordens que já estejam alocadas."
                                    "Caso seja omitido ou seu valor seja 0 (zero), então todas as ordens do "
                                    "usuário logado serão retornadas.",
                        "subtags": [
                            {
                                "tag": 79,
                                "name": "AllocAccount",
                                "required": True,
                                "datatype": str,
                                "comments": "Código da conta. Obrigatório caso NoAllocs > 0."
                            },
                            {
                                "tag": 1301,
                                "name": "MarketID",
                                "required": True,
                                "datatype": int,
                                "comments": "Identificador do mercado. Valores possíveis: XBMF = BM&F "
                            }
                        ]
                    },
                    {
                        "tag": 5487,
                        "name": "NoOrdStatus",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de OrdStatus possíveis que serão retornados na consulta. Caso seja "
                                    "omitido ou seu valor seja 0 (zero), serão retornadas as ordens de todos os "
                                    "status.",
                        "subtags": [
                            {
                                "tag": 39,
                                "name": "OrdStatus",
                                "required": False,
                                "datatype": str,
                                "comments": "Status da ordem. Valores possíveis: Obrigatório caso NoOrdStatus > "
                                            "0. 0 = New (Recebida) 1 = Partially Filled (Parcialmente Executada) "
                                            "2 = Filled (Completamente Executada) 4 = Canceled (Cancelada) 5 = "
                                            "Replaced (Editada) 6 = PendingCancel (Cancelamento Pendente) 8 = "
                                            "Rejected (Rejeitada) 9 = Suspended (Suspensa/Pendente – esperando "
                                            "abertura do mercado para ser enviada) A = Pending New (Pendente) C = "
                                            "Expired (Expirada) E = Pending Replace (Esperando Edição) ",
                                "domain": ['0', '1', '2', '4', '5', '6', '8', '9', 'A', 'C', 'E']
                            }
                        ]
                    },
                    {
                        "tag": 10013,
                        "name": "NoOrdType",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de OrdType possíveis que serão retornados na consulta. Caso seja "
                                    "omitido ou seu valor seja 0 (zero), serão retornadas as ordens de todos os "
                                    "tipos.",
                        "subtags": [
                            {
                                "tag": 40,
                                "name": "OrdType",
                                "required": False,
                                "datatype": str,
                                "comments": "Obrigatório se o NoOrdType for maior que zero. Tipo da ordem. Pode "
                                            "ter um dos seguintes valores: 2 = Limite 4 = Stop Limit K = Market "
                                            "with leftover as Limit ",
                                "domain": ['2', '4', 'K']
                            }
                        ]
                    },
                    {
                        "tag": 10595,
                        "name": "NoOriginOrdType",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de OrdType de Ordem origem possíveis que serão retornados na "
                                    "consulta. Caso seja omitido ou seu valor seja 0 (zero), serão retornadas as "
                                    "ordens de todos os tipos de origem.",
                        "subtags": [
                            {
                                "tag": 40,
                                "name": "OrdType",
                                "required": False,
                                "datatype": str,
                                "comments": "Obrigatório se o NoOrdType for maior que zero. Tipo da ordem. Pode "
                                            "ter um dos seguintes valores: 2 = Limite 4 = Stop Limit K = Market "
                                            "with leftover as Limit ",
                                "domain": ['2', '4', 'K']
                            }
                        ]
                    },
                    {
                        "tag": 916,
                        "name": "StartDate",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "comments": "Data inicial, considerando horário também."
                    },
                    {
                        "tag": 917,
                        "name": "EndDate",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "comments": "Data final, considerando horário também."
                    },
                    {
                        "tag": 20103,
                        "name": "QueryType",
                        "required": False,
                        "datatype": str,
                        "comments": "0 – Day (Apenas do dia) 1 – History (Todas as ordens).",
                        "domain": [0, 1]
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": False,
                        "datatype": str,
                        "comments": "Direção da ordem. Valores válidos: 1 – Compra 2 – Venda.",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 10264,
                        "name": "OrderTag",
                        "required": False,
                        "datatype": str,
                        "lenght": 50,
                        "comments": "Tag (observação) informada para a ordem. Para ordens enviadas ao mercado "
                                    "através de uma sessão EntryPoint seu valor é repassado para o campo Memo ("
                                    "5149). Obs.: No EntryPoint são permitidos no máximo 50 caracteres para este "
                                    "campo."
                    },
                    {
                        "tag": 35004,
                        "name": "StartDateYYYYMMDD",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d').date()",
                        "lenght": 50,
                        "comments": "Data inicial, considerando apenas ano, mês e dia."
                    },
                    {
                        "tag": 35005,
                        "name": "EndDateYYYYMMDD",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d').date()",
                        "lenght": 50,
                        "comments": "Data final, considerando apenas ano, mês e dia."
                    },
                    {
                        "tag": 9933,
                        "name": "ApplicationName",
                        "required": True,
                        "datatype": str,
                        "comments": "Tag que informa o identificador da aplicação utilizada pelo usuário(sessão)."
                                    "As ordens enviadas poderão ser filtradas por esseidentificador."
                    }
                ]
            },
            {
                "MsgType": "Q",
                "type": "Don’t Know Trade DK",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 37,
                        "name": "OrderID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da ordem como definido pelo roteador."
                    },
                    {
                        "tag": 11,
                        "name": "ExecID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único da mensagem de execução definido pelo roteador."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 54,
                        "name": "Side",
                        "required": True,
                        "datatype": str,
                        "comments": "Direção da ordem. Valores válidos: 1 = Compra 2 = Venda ",
                        "domain": [1, 2]
                    },
                    {
                        "tag": 38,
                        "name": "OrderQty",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de contratos ordenados."
                    },
                    {
                        "tag": 127,
                        "name": "DkReason",
                        "required": True,
                        "datatype": str,
                        "comments": "Código que identifica o motivo de rejeição. Os valores válidos são: A = "
                                    "Unknow Symbol B = Wrong Side C = Quantity Exceeds Order D = No Matching "
                                    "Order E = Price Exceeds Limit F = Calculation Difference Z = Other.",
                        "domain": ['A', 'B', 'C', 'D', 'E', 'F', 'Z']
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Descrição do erro. Condicionalmente obrigatório no caso de DkReason = Z ("
                                    "Other)."
                    }
                ]
            },
            {
                "MsgType": "j",
                "type": "Business Message Reject",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 45,
                        "name": "RefSeqNum",
                        "required": False,
                        "datatype": int,
                        "comments": "MsgSeqNum da mensagem rejeitada."
                    },
                    {
                        "tag": 372,
                        "name": "RefMsgType",
                        "required": True,
                        "datatype": str,
                        "comments": "Valor do campo de identificação da mensagem referenciada, no nível de "
                                    "aplicação. Requerido a não ser que o campo de identificação correspondente "
                                    "não tenha sido identificado."
                    },
                    {
                        "tag": 379,
                        "name": "BusinessRejectRefID",
                        "required": False,
                        "datatype": str,
                        "comments": "Valor do campo de identificação da mensagem referenciada, no nível de "
                                    "aplicação. Requerido a não ser que o campo de identificação correspondente "
                                    "não tenha sido identificado."
                    },
                    {
                        "tag": 380,
                        "name": "BusinessRejectReason",
                        "required": True,
                        "datatype": int,
                        "comments": "Código de identificação do motivo de rejeição. Valores válidos: 0 = Outro 1 "
                                    "= Identificador Inválido 2 = Instrumento Inválido 3 = Tipo de mensagem não "
                                    "suportado 4 = Aplicação não disponível 5 = Falta de campo condicionalmente "
                                    "requerido.",
                        "domain": [0, 1, 2, 3, 4, 5]
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Mensagem com explicação do motivo de rejeição, se necessário."
                    }
                ]
            },
            {
                "MsgType": "BD",
                "type": "Network Counterparty System Status Response",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 937,
                        "name": "NetworkStatusResponseType",
                        "required": True,
                        "datatype": int,
                        "comments": "Indentifica o tipo de resposta. Valores possíveis: 1=Full."
                    },
                    {
                        "tag": 932,
                        "name": "NetworkResponseID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único para a resposta do servidor."
                    },
                    {
                        "tag": 936,
                        "name": "NoCompIDs",
                        "required": True,
                        "datatype": int,
                        "comments": "Número de CompIDs dentro do Repeating Group.",
                        "subtags": [
                            {
                                "tag": 930,
                                "name": "CompID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica qual o servidor.",
                            },
                            {
                                "tag": 928,
                                "name": "StatusValue",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o Status do servidor. Valores possíves: 1= Connected 2= "
                                            "NotConnectedDownExpectedUp 3= NotConnectedDownExpectedDown 4= "
                                            "InProcess.",
                                "domain": [1, 2, 3, 4]
                            },
                            {
                                "tag": 929,
                                "name": "StatusText",
                                "required": True,
                                "datatype": str,
                                "comments": "Texto aberto que determina o status do servidor.",
                            }
                        ]
                    }
                ]
            },
            {
                "MsgType": "AN",
                "type": "Request for Positions",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 710,
                        "name": "PosReqID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único da requisição do portifólio da conta."
                    },
                    {
                        "tag": 724,
                        "name": "PosReqType",
                        "required": True,
                        "datatype": int,
                        "comments": "Tipo da requisição. Valores possíveis: 0 = Positions.",
                        "default": 0
                    },
                    {
                        "tag": 263,
                        "name": "SubscriptionRequestType",
                        "required": True,
                        "datatype": str,
                        "comments": "Forma de atualização. Valores possíveis: 0 = Snapshot, "
                                    "1 = Snapshot Update, 2 = Unsubscribe.",
                        "domain": ['0', '1', '2']
                    },
                    {
                        "tag": 10552,
                        "name": "OpenQtyFilter",
                        "required": False,
                        "datatype": str,
                        "comments": "Filtro de quantidades em aberto. Valores possíveis: 0 = Quantidades em aberto, "
                                    "1 = Somente executadas.",
                        "domain": ['0', '1']
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating group que contém o identificador do usuário que fez a requisição. "
                                    "Deve ter valor 1.",
                        "default": 1,
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do usuário que fez a requisição."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: "
                                            "D = Proprietary/Custom code",
                                "default": 'D'
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 3 = ClientID",
                                "default": 3
                            }
                        ]
                    },
                    {
                        "tag": 1,
                        "name": "Account",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da conta. Valores possíveis: 1 = AccountCustomer",
                        "domain": '1'
                    },
                    {
                        "tag": 1301,
                        "name": "MarketID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador do mercado. Valores possíveis: XBSP = BOVESPA",
                        "domain": 'XBSP'
                    },
                    {
                        "tag": 715,
                        "name": "ClearingBusinessDate",
                        "required": True,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d').date()",
                        "comments": "Data de referência"
                    },
                    {
                        "tag": 60,
                        "name": "TransactTime",
                        "required": True,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                        "calculated": True,
                        "comments": "Data/Hora da criação da ordem."
                    },
                    {
                        "tag": 11123,
                        "name": "FilterType",
                        "required": False,
                        "datatype": int,
                        "comments": "Indica busca apenas de custódia inicial."
                    }
                ]
            },
            {
                "MsgType": "AP",
                "type": "Position Report",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 721,
                        "name": "PosMainRptID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único do relatório de posições."
                    },
                    {
                        "tag": 710,
                        "name": "PosReqID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador único da requisição do portifólio da conta."
                    },
                    {
                        "tag": 727,
                        "name": "TotalNumPosReports",
                        "required": True,
                        "datatype": int,
                        "comments": "Total de relatórios a serem enviados.",
                        "default": 0
                    },
                    {
                        "tag": 728,
                        "name": "PosReqResult",
                        "required": True,
                        "datatype": int,
                        "comments": "Resultado da requisição. Valores possíveis: 0 = Requisição válida, "
                                    "1 = Requisição inválida ou não suportada, 2 = Nenhuma posição encontrada, "
                                    "3 = Não autorizado, 4 = Não suportado, 5 = Conta não encontrada, 99 = Outro",
                        "domain": [0, 1, 2, 3, 4, 5, 99]
                    },
                    {
                        "tag": 715,
                        "name": "ClearingBusinessDate",
                        "required": True,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d').date()",
                        "comments": "Data de referência.",
                        "domain": ['0', '1']
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating group que contém o identificador do usuário que fez a requisição. "
                                    "Deve ter valor 1.",
                        "default": 1,
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do usuário que fez a requisição."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: "
                                            "D = Proprietary/Custom code",
                                "default": 'D'
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 3 = ClientID",
                                "default": 3
                            }
                        ]
                    },
                    {
                        "tag": 1,
                        "name": "Account",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da conta. Valores possíveis: 1 = AccountCustomer",
                        "domain": '1'
                    },
                    {
                        "tag": 1301,
                        "name": "MarketID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador do mercado."
                    },
                    {
                        "tag": 581,
                        "name": "AccountType",
                        "required": True,
                        "datatype": int,
                        "comments": "Tipo da conta. Valores possíveis: 1 = AccountCustomer.",
                        "default": 1
                    },
                    {
                        "tag": 10094,
                        "name": "TotalPurchaseValue",
                        "required": False,
                        "datatype": float,
                        "comments": "Valor total de compra execudada."
                    },
                    {
                        "tag": 10095,
                        "name": "TotalNotExecPurchaseValue",
                        "required": False,
                        "datatype": float,
                        "comments": "Valor total de compra em aberto."
                    },
                    {
                        "tag": 10096,
                        "name": "TotalSaleValue",
                        "required": False,
                        "datatype": float,
                        "comments": "Valor total de venda executada."
                    },
                    {
                        "tag": 10097,
                        "name": "TotalNotExecSaleValue",
                        "required": False,
                        "datatype": float,
                        "comments": "Valor total de venda em aberto."
                    },
                    {
                        "msg": "ident",
                        "obs": "Aqui entra o bloco ident..."
                    },
                    {
                        "tag": 730,
                        "name": "SettlPrice",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço médio de compra quando a custódia é positiva, ou preço médio de venda "
                                    "quando a custódia é negativa. Obrigatório quando PosReqResult for igual a 0."
                    },
                    {
                        "tag": 731,
                        "name": "SettlPriceType",
                        "required": False,
                        "datatype": int,
                        "comments": "Tipo do preço médio. Valores possíveis: 1 = Final Obrigatório quando "
                                    "PosReqResult for igual a 0. "
                    },
                    {
                        "tag": 734,
                        "name": "PriorSettlPrice",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço médio anterior de compra quando a custódia é positiva, ou preço médio "
                                    "anterior de venda quando a custódia é negativa. Obrigatório quando PosReqResult "
                                    "for igual a 0."
                    },
                    {
                        "tag": 702,
                        "name": "NoPositions",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de posições.",
                        "subtags": [
                            {
                                "tag": 703,
                                "name": "PosType",
                                "required": False,
                                "datatype": str,
                                "comments": "Identificador do tipo de quantidade retornada. Valores possíveis: SOD = "
                                            "Quantidade do início do dia, CRQ = Quantidade corrente, EPQ = Quantidade "
                                            "comprada executada, ESQ = Quantidade vendida executada, "
                                            "EPRRQ = Quantidade comprada executada de repasse recebido, "
                                            "ESRRQ = Quantidade vendida executada de repasse recebido, "
                                            "NEPQ = Quantidade comprada não executada, NESQ = Quantidade vendida não "
                                            "executada, BSV = Quantidade bloqueada, D0Q = Quantidade D0, "
                                            "D1Q = Quantidade D1, D2Q = Quantidade D2, D3Q = Quantidade D3, "
                                            "BTC = Quantidade Tomada de BTC, GBTC = Quantidade Doada de BTC, "
                                            "FBTC = Quantidade de BTC Livre, TMSQ = Quantidade de Liquidação de "
                                            "Termo, OPTQ = Quantidade aberta executada(net), OPDQ = Quantidade aberta "
                                            "executada em daytrade, OPCQ = Quantidade aberta executada em custódia, "
                                            "BAVP = Preço médio de compra, SAVP = Preço médio de venda, "
                                            "WWQTY = Quantidade na carteira de garantia, QCEX = Quantidade executada "
                                            "comprada daytrade, QVEX = Quantidade executada vendida daytrade, "
                                            "QTCA = Quantidade não executada de compra daytrade, QTVA = Quantidade "
                                            "não executada de venda daytrade.",
                                "domain": ['SOD', 'CRQ', 'EPQ', 'ESQ', 'EPRRQ', 'ESRRQ', 'NEPQ', 'NESQ', 'BSV', 'D0Q',
                                           'D1Q', 'D2Q', 'D3Q', 'BTC', 'GBTC', 'FBTC', 'TMSQ', 'OPTQ', 'OPDQ', 'OPCQ',
                                           'BAVP', 'SAVP', 'WWQTY', 'QCEX', 'QVEX', 'QTCA', 'QTVA']
                            },
                            {
                                "tag": 704,
                                "name": "LongQty",
                                "required": False,
                                "datatype": int,
                                "comments": "Quantidade do tipo especificado."
                            }
                        ]
                    },
                    {
                        "tag": 753,
                        "name": "NoPosAmt",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de valores.",
                        "subtags": [
                            {
                                "tag": 707,
                                "name": "PosAmtType",
                                "required": False,
                                "datatype": str,
                                "comments": "Identificador do tipo de valor retornado. Valores possíveis: CIP = Preço "
                                            "corrente do instrumento, PCP = Preço de fechamento do dia anterior, "
                                            "VADJ = Valor do montante ajustado, TPV =Montante total de compra, "
                                            "TSV = Montante total de venda, CVA= Montante do valor corrente, "
                                            "OPLX = L/P aberto, CLPLX = L/P fechado, OAVT = Preço médio aberto do "
                                            "dia, BRKV = Ponto de equilibrio.",
                                "domain": ['CIP', 'PCP', 'VADJ', 'TPV', 'TSV', 'CVA', 'OPLX', 'CLPLX', 'OAVT', 'BRKV']
                            },
                            {
                                "tag": 708,
                                "name": "PosAmt",
                                "required": False,
                                "datatype": str,
                                "comments": "Valor do tipo especificado."
                            }
                        ]
                    },
                    {
                        "tag": 10098,
                        "name": "LastTradeDateTime",
                        "required": False,
                        "datatype": "datetime.strptime('{0}', '%Y%m%d').date()",
                        "comments": "Data/hora da última negociação."
                    },
                    {
                        "tag": 20056,
                        "name": "CurrentQty",
                        "required": False,
                        "datatype": float,
                        "comments": "Quantidade atual."
                    },
                    {
                        "tag": 10144,
                        "name": "OpenBuyQty",
                        "required": False,
                        "datatype": int,
                        "comments": "Quantidade aberta de compra."
                    },
                    {
                        "tag": 10146,
                        "name": "OpenSellQty",
                        "required": False,
                        "datatype": int,
                        "comments": "Quantidade aberta de venda."
                    },
                    {
                        "tag": 20049,
                        "name": "BlockedSellQty",
                        "required": False,
                        "datatype": float,
                        "comments": "Quantidade de venda bloqueada."
                    },
                    {
                        "tag": 10379,
                        "name": "QuotationForm",
                        "required": False,
                        "datatype": int,
                        "comments": "Forma de cotação do ativo."
                    },
                    {
                        "tag": 10700,
                        "name": "BTCSettlPrice",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço Médio da posição tomadade BTC."
                    },
                    {
                        "tag": 10701,
                        "name": "BTCSettlPrice",
                        "required": False,
                        "datatype": float,
                        "comments": "Preço Médio da posição doada de BTC."
                    },
                    {
                        "tag": 10188,
                        "name": "LeveragebleQuote",
                        "required": False,
                        "datatype": bool,
                        "comments": "Indica se o ativo está alavancado na lista de papéis alavancados."
                    },
                    {
                        "tag": 11197,
                        "name": "IsAggregateOnLeverage",
                        "required": False,
                        "datatype": bool,
                        "comments": "Não calcular custódia desagiada/leverage quando tiver valor."
                    }
                ]
            },
            {
                "MsgType": "U67",
                "type": "Financial Account Information Request",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 10318,
                        "name": "FinancialAccountReqID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador único da requisição de Financial Account. Deve ser único por dia "
                                    "ou sessão e definido pelo iniciador. "
                    },
                    {
                        "tag": 1,
                        "name": "Account",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da conta."
                    },
                    {
                        "tag": 1301,
                        "name": "MarketID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador do mercado.",
                        "domain": ['XBMF', 'XBSP']
                    },
                    {
                        "tag": 263,
                        "name": "SubscriptionRequestType",
                        "required": True,
                        "datatype": str,
                        "comments": "Forma de atualização. Valores possíveis: 0 = Snapshot, 1 = Snapshot Update, "
                                    "2 = Unsubscribe. ",
                        "domain": ['0', '1', '2']
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": True,
                        "datatype": int,
                        "comments": "Repeating group que contém o identificador do usuário que fez a requisição. "
                                    "Deve ter valor 1.",
                        "default": 1,
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do usuário que fez a requisição."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: "
                                            "D = Proprietary/Custom code",
                                "default": 'D'
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 3 = ClientID",
                                "default": 3
                            }
                        ]
                    },
                    {
                        "tag": 10612,
                        "name": "BalanceComposition",
                        "required": False,
                        "datatype": int,
                        "comments": "Campo que indica se deverá retornar somente os saldos iniciais de cada conta "
                                    "ligada à conta financeira. Valores aceitos: 0 = All.",
                        "default": 0
                    },
                    {
                        "tag": 11123,
                        "name": "FilterType",
                        "required": False,
                        "datatype": int,
                        "calculated": True,
                        "comments": "Indica busca apenas por dados reduzidos."
                    }
                ]
            },
            {
                "MsgType": "U68",
                "type": "Financial Account Information Report",
                "msg_body_required": ["header", "footer"],
                "tags": [
                    {
                        "tag": 10318,
                        "name": "FinancialAccountReqID",
                        "required": True,
                        "datatype": str,
                        "comments": "Eco do identificador único da requisição de financial account."
                    },
                    {
                        "tag": 1301,
                        "name": "MarketID",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador do mercado. Valores possíveis: XBMF = BM&F, XBSP = BOVESPA",
                        "domain": ['XBMF', 'XBSP']
                    },
                    {
                        "tag": 1,
                        "name": "Account",
                        "required": True,
                        "datatype": str,
                        "comments": "Identificador da conta.",
                        "domain": '1'
                    },
                    {
                        "tag": 10263,
                        "name": "FinancialAccount",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador da conta financeira."
                    },
                    {
                        "tag": 10331,
                        "name": "GroupID",
                        "required": False,
                        "datatype": str,
                        "comments": "Identificador do grupo ao qual à conta financeira pertence."
                    },
                    {
                        "tag": 453,
                        "name": "NoPartyID",
                        "required": False,
                        "datatype": int,
                        "comments": "Repeating group que contém o identificador do usuário que fez a requisição. "
                                    "Deve ter valor 1.",
                        "default": 1,
                        "subtags": [
                            {
                                "tag": 448,
                                "name": "PartyID",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do usuário que fez a requisição."
                            },
                            {
                                "tag": 447,
                                "name": "PartyIDSource",
                                "required": True,
                                "datatype": str,
                                "comments": "Identifica a origem do PartyID. O único valor aceito é: "
                                            "D = Proprietary/Custom code",
                                "default": 'D'
                            },
                            {
                                "tag": 452,
                                "name": "PartyRole",
                                "required": True,
                                "datatype": int,
                                "comments": "Identifica o tipo do participante. Valores aceitos: 3 = ClientID",
                                "default": 3
                            }
                        ]
                    },
                    {
                        "tag": 10319,
                        "name": "FinancialAccountRejReason",
                        "required": False,
                        "datatype": int,
                        "comments": "Motivo da rejeição. Valores possíveis: 0 = Requisição inconsistente, 1 = Sem "
                                    "permissão, 2 = Usuário não encontrado, 3 = Account inválido, 4 = Outro ("
                                    "Descrição no campo Text 58).",
                        "domain": [0, 1, 2, 3, 4]
                    },
                    {
                        "tag": 58,
                        "name": "Text",
                        "required": False,
                        "datatype": str,
                        "comments": "Texto descrevendo o motivo da rejeição, caso seja necessário."
                    },
                    {
                        "tag": 753,
                        "name": "NoPosAmt",
                        "required": False,
                        "datatype": int,
                        "comments": "Número de posições.",
                        "subtags": [
                            {
                                "tag": 707,
                                "name": "PosAmtType",
                                "required": True,
                                "datatype": str,
                                "comments": "Identificador do tipo de valor retornado. Valores possíveis: IPRBA = "
                                            "ProjectBalance', INBA = InitialBalance', CED0 = CreditEntryDay0', "
                                            "CED1 = CreditEntryDay1', CED2 = CreditEntryDay2', "
                                            "CED3 = CreditEntryDay3', DED0 = DebitEntryDay0', DED1 = DebitEntryDay1', "
                                            "DED2 = DebitEntryDay2', DED3 = DebitEntryDay3', LEVE = Leverage', "
                                            "FNLE = FinancialLeverage', OVCR = OverdraftCredit', "
                                            "DFAT = DailyFinancialActivities', AVBA = AvailableBalance', "
                                            "CHLT = CashLimit', OPLT = OptionLimit', "
                                            "NEPA = NotExecutedPurchaseAmmount', NESA = NotExecutedSellAmmount', "
                                            "BCKA = BlockedAmmount', OVAM = OverdraftAmmount', "
                                            "POVA = PotencialOverdraftAmmount', BCMB = BalanceCashMarketBovespa', "
                                            "BCMF  = BalanceCashMarketBMF', BUOP = BalanceUncoveredOperation', "
                                            "BOPT = BalanceOptions', OVLT = OverdraftLimit', "
                                            "BSCC = BovespaCashOperationCredit', "
                                            "BSOC = BovespaOptionOperationCredit', BMFC = BMFOperationCredit', "
                                            "BMBM = BMFBlockedMargin', ADD0 = AdjustDay0', ADD1 = AdjustDay1', "
                                            "BEBM = BMFExecutedBlockedMargin', BNBM = BMFNotExecutedBlockedMargin', "
                                            "BNEP = BMFNotExecutedPurchaseAmmount', "
                                            "BNES = BMFNotExecutedSellAmmount', OPAM = OpenedPurchaseAmmount', "
                                            "OSAM = OpenedSellAmmount', BOPF = BalanceOptionsOrFuture', "
                                            "BMFL = BMFLimit', BUNM = BMFUnblockedMargin', DLMG = DownLockMargin', "
                                            "INTR = Interest', IOFV = Iof', AIOF = AdditionalIof', "
                                            "LVPP = LeveragePercentageProjected', TSPV = TotalStockPortfolioValue', "
                                            "TOPV = TotalOptionPortfolioValue', TBPV = TotalBmfPortfolioValue', "
                                            "FOOA = FilledOverdraftOptionAmmount', "
                                            "NOOA = NotExecutedOverdraftOptionAmmount', CHOP = Cash OpenPurchases', "
                                            "OPOP = OptionsOpenPurchases', CHOS = CashOpenSells', "
                                            "OPOS = OptionsOpenSells', CHEP = CashExecutedPurchases', "
                                            "OPEP = OptionsExecutedPurchases', CHES = CashExecutedSells', "
                                            "OPES = OptionsExecutedSells', CHPL = CashPurchaseLimit', "
                                            "OPPL = OptionsPurchaseLimit', CHSL = CashSellLimit', "
                                            "OPSL = OptionsSellLimit', CHPA = CashPurchaseAmmount', "
                                            "CHSA = CashSellAmmount', OPPA = OptionsPurchaseAmmount', "
                                            "OPSA = OptionsSellAmmount', INPRBA = InitialProjectedBalance', "
                                            "INLT = InitialLimit', INLTB = InitialLimitBmf', "
                                            "INSPV = InitialStockPortfolioValue', "
                                            "INOPV = InitialOptionsPortfolioValue', "
                                            "INBPV = InitialBmfPortfolioValue', OPL = OpenProfitLoss', "
                                            "CLPL = ClosedProfitLoss', INEQ = InitialEquity', INEQAC = initialEquity "
                                            "na zeragem automatica', TOEQ = TotalEquity', GNMA = GeneralMargin', "
                                            "OPMA = OptionsMargin', IPOB = IpoBlocked', LILO = LeverageOptionsLimit', "
                                            "BMCL = BMFCashLimit', BSOPCR = BSLimitOperationCredit', "
                                            "TRDI = TreasuryDirect', INFU = InvestmentFunds', CLFU = ClubsAndFunds', "
                                            "TOSPV = TotalOnlineStockPortfolioValue', "
                                            "TOOPV = TotalOnlineOptionsPortfolioValue', "
                                            "CESD1 = StartCreditEntryDay1', CESD2 = StartCreditEntryDay2', "
                                            "DESD1 = StartDebitEntryDay1', DESD2 = StartDebitEntryDay2', "
                                            "CHLL = CashLeveragedLimit', OPLL = OptionsLeveragedLimit', "
                                            "BMFLL = BmfLeveragedLimit', UNQL = UniqueLimit', "
                                            "BLVL = BlockedValueLimit', OPLDT = OpenProfitLossDayTrade', "
                                            "CPLDT = ClosedProfitLossDayTrade', BPOM = BmfPurchaseOpenMargin', "
                                            "BPEM = BmfPurchaseExecutedMargin', BSOM = BmfSellOpenMargin', "
                                            "BSEM = BmfSellExecutedMargin', BMFPL = BmfPurchaseLimit', "
                                            "BMFSL = BmfSellLimit', BMFPA = BmfPurchaseAmmount', "
                                            "BMFSA = BmfSellAmmount', BPAD = BmfPositionAdjust', "
                                            "BTAD = BmfTradingAdjust', DTAD = DayTradeAdjustment', "
                                            "INFUC = FixedIncomeConsidered', CLFUC = ClubsConsidered', "
                                            "TOBPV = TotalOnlineBmfPortfolioValue', FNDS = Funds', "
                                            "FNDSC = FundsConsidered', DVDS = Dividends', BSPWT = XbspWarrantyTotal', "
                                            "BMFWT = XbmfWarrantyTotal', BMFMA = XbmfMarginAvailable', "
                                            "BGBMF = BrokerageXbmf', BGBSP = BrokerageXbsp', TAX = Taxes', "
                                            "EMOL = Emolument', ACMT = AccountMarginTotal', "
                                            "ACMU = AccountMarginUsed', OPLVG = QuoteOptionLeverage', "
                                            "EQLVG = EquityLeveraged', D1CDT = D1CreditDaytrade', "
                                            "D1DDT = D1DebitDaytrade', D3CDT = D3CreditDaytrade', "
                                            "D3DDT = D3DebitDaytrade', D1CPO = D1CreditPosition', "
                                            "D1DPO = D1DebitPosition', D3CPO = D3CreditPosition', "
                                            "D3DPO = D3DebitPosition', NPA = NegativePositionAmount', "
                                            "NOPA = NegativeOptPositionAmount', CRDL = CreditLimit', "
                                            "WREQ = WarrantyRequired', WDEP = WarrantyDeposited', REFIA = fixed "
                                            "income application used', FUNDA = Aplicações em fundos utilizado', "
                                            "TEDIA = Aplicações em tesouro direto utilizado', TOEQM =  Patrimônio "
                                            "Online + Margem cheia', BPESM =  Compras executadas BMF com Margem "
                                            "cheia', BSESM = Vendas executadas BMF com Margem cheia', CUPL = Lucro ou "
                                            "perda da custodia', RQDM = Margem requerida daytrade', CBMA = Devolver "
                                            "margem teórica máxima BMF ao encerrar uma posição', BRKV = Ponto de "
                                            "equilíbrio para saída de posição', CLPLO = Lucro ou perda fechados da "
                                            "operação', PREV = PrevidênciaPREVC = Previdência considerada', "
                                            "TRDIC = Tesouro direto considerado', OOAC = Valor em dinheiro a ser "
                                            "retirado do prêmio, ordem aberta no book para opção', OMUL = Devolver "
                                            "margem teórica máxima BTC-T ao encerrar uma posição', VTAP = Valor em "
                                            "trânsito para aplicações.",
                                "domain": ['PRBA', 'INBA', 'CED0', 'CED1', 'CED2', 'CED3', 'DED0', 'DED1', 'DED2',
                                           'DED3', 'LEVE', 'FNLE', 'OVCR', 'DFAT', 'AVBA', 'CHLT', 'OPLT', 'NEPA',
                                           'NESA', 'BCKA', 'OVAM', 'POVA', 'BCMB', 'BCMF', 'BUOP', 'BOPT', 'OVLT',
                                           'BSCC', 'BSOC', 'BMFC', 'BMBM', 'ADD0', 'ADD1', 'BEBM', 'BNBM', 'BNEP',
                                           'BNES', 'OPAM', 'OSAM', 'BOPF', 'BMFL', 'BUNM', 'DLMG', 'INTR', 'IOFV',
                                           'AIOF', 'LVPP', 'TSPV', 'TOPV', 'TBPV', 'FOOA', 'NOOA', 'CHOP', 'OPOP',
                                           'CHOS', 'OPOS', 'CHEP', 'OPEP', 'CHES', 'OPES', 'CHPL', 'OPPL', 'CHSL',
                                           'OPSL', 'CHPA', 'CHSA', 'OPPA', 'OPSA', 'INPRBA', 'INLT', 'INLTB', 'INSPV',
                                           'INOPV', 'INBPV', 'OPL', 'CLPL', 'INEQ', 'INEQAC', 'TOEQ', 'GNMA', 'OPMA',
                                           'IPOB', 'LILO', 'BMCL', 'BSOPCR', 'TRDI', 'INFU', 'CLFU', 'TOSPV', 'TOOPV',
                                           'CESD1', 'CESD2', 'DESD1', 'DESD2', 'CHLL', 'OPLL', 'BMFLL', 'UNQL', 'BLVL',
                                           'OPLDT', 'CPLDT', 'BPOM', 'BPEM', 'BSOM', 'BSEM', 'BMFPL', 'BMFSL', 'BMFPA',
                                           'BMFSA', 'BPAD', 'BTAD', 'DTAD', 'INFUC', 'CLFUC', 'TOBPV', 'FNDS', 'FNDSC',
                                           'DVDS', 'BSPWT', 'BMFWT', 'BMFMA', 'BGBMF', 'BGBSP', 'TAX', 'EMOL', 'ACMT',
                                           'ACMU', 'OPLVG', 'EQLVG', 'D1CDT', 'D1DDT', 'D3CDT', 'D3DDT', 'D1CPO',
                                           'D1DPO', 'D3CPO', 'D3DPO', 'NPA', 'NOPA', 'CRDL', 'WREQ', 'WDEP', 'REFIA',
                                           'FUNDA', 'TEDIA', 'TOEQM', 'BPESM', 'BSESM', 'CUPL', 'RQDM', 'CBMA', 'BRKV',
                                           'CLPLO', 'PREV', 'TRDIC', 'OOAC', 'OMUL', 'VTAP']
                            },
                            {
                                "tag": 708,
                                "name": "PosAmt",
                                "required": False,
                                "datatype": str,
                                "comments": "Valor do tipo especificado."
                            }
                        ]
                    },
                    {
                        "tag": 10061,
                        "name": "NoAccounts",
                        "required": False,
                        "datatype": int,
                        "comments": "Grupo que contém cada conta relacionada à conta financeira, seu mercado e seu "
                                    "saldo inicial.",
                        "subtags": [
                            {
                                "tag": 10613,
                                "name": "ClientAccountID",
                                "required": False,
                                "datatype": str,
                                "comments": "ID da conta recuperada."
                            },
                            {
                                "tag": 10614,
                                "name": "ClientMarketID",
                                "required": False,
                                "datatype": str,
                                "comments": "ID do mercado da conta."
                            },
                            {
                                "tag": 10615,
                                "name": "InitialBalanceAccount",
                                "required": False,
                                "datatype": float,
                                "comments": "Valor do saldo inicial da conta."
                            }
                        ]
                    }
                ]
            }
        ]
    }

    def get_layout(self, msg_type: str) -> list:
        sel_df = {}
        for df in self.oms_format.get("MsgTypes", []):
            if msg_type == df.get("MsgType"):
                sel_df = df
                break

        lst_ret_layout = []
        if "header" in sel_df.get("msg_body_required"):
            lst_ret_layout.extend(self.oms_format.get("msg").get("header"))

        for tag in sel_df.get("tags"):
            if "msg" not in tag:
                lst_ret_layout.append(tag)
            else:
                lst_ret_layout.extend(self.oms_format.get("msg").get("ident"))

        if "footer" in sel_df.get("msg_body_required"):
            lst_ret_layout.extend(self.oms_format.get("msg").get("footer"))

        return lst_ret_layout

    def get_template(self, msg_type: str, lst_ignore: list, required_only=True) -> dict:

        def add_item(i_dtc_template, i_item, i_lst_ignore):
            if i_item.get("name") == 'MsgType':
                i_dtc_template[i_item.get("name")] = msg_type
                i_lst_ignore.append('MsgType')

            if i_item.get("name") not in i_lst_ignore:
                if i_item.get("required", False):
                    i_dtc_template[i_item.get("name")] = \
                        i_item.get("datatype") if i_item.get("default", None) is None else i_item.get("default")

                elif not required_only:
                    i_dtc_template[i_item.get("name")] = "Not required " + str(i_item.get("datatype")) \
                        if i_item.get("default", None) is None else i_item.get("default")

            if i_item.get("calculated", False) and i_item.get("name") not in i_lst_ignore:
                i_dtc_template[i_item.get("name")] = "will be calculated"

        lst_layout = self.get_layout(msg_type)

        dtc_template = {}
        for item in lst_layout:
            add_item(dtc_template, item, lst_ignore)
            for sitem in item.get("subtags", []):
                add_item(dtc_template, sitem, lst_ignore)

        return dtc_template
