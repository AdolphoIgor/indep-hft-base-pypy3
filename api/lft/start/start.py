class Start:

    def __init__(self, **kwargs):
        self._market_data = kwargs.get("mkt_dt", [])

    def start(self) -> list:
        pass
