## A sessão "algos" do json de configuração tem as seguintes caracteristicas e regras:

```
"algos": [
  {
    "id": 0,
    "name": "Long-PETR3|Short-PETR4",
    "enabled": true,
    "algo_class": "LFT",
    "threads": [
      {
        "symbol": "PETR4",
        "instruments": [
          "T"
        ],
        "oms_id": 0,
        "broker_id": 191,
        "start_class": "Opening",
        "start_parameters": {
          "side": "S",
          "order_qty": 10000,
          "perc_spread_order_at_market": 0.05
        }
      },
      {
        "symbol": "PETR3",
        "instruments": [
          "T"
        ],
        "oms_id": 0,
        "start_class": "Opening",
        "start_parameters": {
          "side": "B",
          "order_qty": 10000
        }
      }
    ],
    "stop_class": "PercTrailingStop",
    "stop_parameters": {
      "perc_trailing": 0.02,
      "inc_trailing": 0.0,
      "stop_limit": 500.00
    }
  },
  {
    "id": 1,
    "name": "Long-BOVA11|Short-INDFUT",
    "enabled": true,
    "algo_class": "LFT",
    "threads": [
      {
        "symbol": "BOVA11",
        "instruments": [
          "T"
        ],
        "oms_id": 0,
        "start_class": "Opening",
        "start_parameters": {
          "side": "S",
          "order_qty": 2500
        }
      },
      {
        "symbol": "INDFUT",
        "instruments": [
          "T"
        ],
        "oms_id": 0,
        "start_class": "Opening",
        "start_parameters": {
          "side": "B",
          "order_qty": 5
        }
      }
    ],
    "stop_class": "PercTrailingStop",
    "stop_parameters": {
      "perc_trailing": 0.09,
      "inc_trailing": 0.0,
      "stop_limit": 500.00
    }
  },
  {
    "id": 2,
    "name": "Long-VALE3",
    "enabled": true,
    "algo_class": "LFT",
    "threads": [
      {
        "symbol": "VALE3",
        "instruments": [
          "T"
        ],
        "oms_id": 0,
        "start_class": "Opening",
        "start_parameters": {
          "side": "S",
          "order_qty": 10000
        }
      }
    ],
    "stop_class": "PercTrailingStop",
    "stop_parameters": {
      "perc_trailing": 0.02,
      "inc_trailing": 0.0,
      "stop_limit": 500.00
    }
  }
]
```

* Cada elemento dentro da lista "algos": [] representa um algoritmo (robô) a ser executado.
* O campo name deve ser composto pela posição a ser tomada + mome do ativo.
* Caso o robô opere mais de um ativo, o nome pode ser composto sepadando os termos com um pipe |
* Dentro da lista "threads": [] temos as configurações individualizadas de cada ponta operada pelo robô.
* Cada thread pode ter seu stop_limit individualizado mas caso deseje-se uma configuração stop_limit aplicada
  simultaneamente ao conjunto de resultados de todas as pontas, estas configurações devem constar fora do escopo da
  lista "threads": [] pelo emprego das configurações "is_stop_limit_global": true + "stop_limit": 0.00.
* 