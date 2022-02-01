from api.lft.stop.stop import Stop


class TrailingStop(Stop):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        inc_trailing = float(kwargs.get('inc_trailing', 0.0))
        self.__inc_trailing = inc_trailing if inc_trailing > 0 else 0.0

    def stop(self, **kwargs) -> bool:
        if self._is_position_changed(**kwargs):
            self._stop = super()._stop + self.__inc_trailing

        return super().stop(**kwargs)
