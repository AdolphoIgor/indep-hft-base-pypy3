from api.lft.start.start import Start


class PreOpening(Start):

    def start(self) -> list:
        lst_ret = []
        if len(self._market_data) == 0:
            return lst_ret

        for inst in self._market_data.get("instruments"):
            if inst.get("type", "") == "T":
                sel_inst = inst.get("instrument", {})
                mntm_grupo = sel_inst.get("Fase do grupo do ativo", "")
                mntm_ativo = sel_inst.get("Status BOVESPA", -1)
                lst_ret.append(
                    {
                        "symbol": sel_inst.get("symbol"),
                        "opened": mntm_grupo == "P" and mntm_ativo in [0, 3],
                        "price": sel_inst.get("Preço teórico de abertura", 0.0),
                        "instrument": sel_inst
                    }
                )
                break

        return lst_ret
