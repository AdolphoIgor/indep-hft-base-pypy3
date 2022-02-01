from api.algo_bot import AlgoBot


class LFT(AlgoBot):

    def __init__(self, name=None, daemon=None, *args, **kwargs):
        super().__init__(name=name, daemon=daemon, *args, **kwargs)

    def run(self):
        while True:
            super().tick()
