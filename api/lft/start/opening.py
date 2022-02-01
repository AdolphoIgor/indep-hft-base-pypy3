from api.lft.start.start import Start


class Opening(Start):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._side = kwargs.get("side", "")

    def start(self) -> list:
        lst_ret = []
        if len(self._market_data) == 0:
            return lst_ret

        for inst in self._market_data.get("instruments"):
            if inst.get("type", "") == "T":
                sel_inst = inst.get("instrument", {})
                mntm_grupo = sel_inst.get("Fase do grupo do ativo", "")
                mntm_ativo = sel_inst.get("Status BOVESPA", -1)
                price = sel_inst.get("Compra", 0.0) if self._side == "B" else sel_inst.get("Venda", 0.0)
                lst_ret.append(
                    {
                        "symbol": sel_inst.get("symbol"),
                        "opened": mntm_grupo == "A" and mntm_ativo == 0,
                        "price": price,
                        "instrument": sel_inst
                    }
                )
                break

        return lst_ret
