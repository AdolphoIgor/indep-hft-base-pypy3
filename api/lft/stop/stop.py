class Stop:

    def __init__(self, **kwargs):
        self._start_parameters = kwargs
        self._position = None
        stop = float(kwargs.get('stop_limit', 0.0))
        self._stop = stop if stop > 0 else 0.0

    def stop(self, **kwargs) -> bool:
        return float(kwargs.get("position", -1.0)) <= self._stop

    def _is_position_changed(self, **kwargs) -> bool:
        if self._position is None:
            self._position = kwargs.get("position", 0.0)

        result = self._position != kwargs.get("position", 0.0)

        if result:
            self._position = kwargs.get("position", 0.0)

        return result
