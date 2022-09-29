from api.lft.algo_bot import AlgoBot


class LFT(AlgoBot):

    def __init__(self, name=None, daemon=None, *args, **kwargs):
        super().__init__(name=name, daemon=daemon, *args, **kwargs)
        self._name = name

    def run(self):
        keep_running = True
        while keep_running:
            keep_running = super().tick()
