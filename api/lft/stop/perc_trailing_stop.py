from api.lft.stop.trailing_stop import Stop


class PercTrailingStop(Stop):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        perc_trailing = float(kwargs.get("perc_trailing", 0.0))
        self.perc_trailing = perc_trailing if perc_trailing > 0 else 0.0

    def stop(self, **kwargs) -> bool:
        if self._is_position_changed(**kwargs):
            position = kwargs.get("position", 0.0)
            self._stop = self._stop + round(position * self.perc_trailing, 2)

        return super().stop(**kwargs)
