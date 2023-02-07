from api.jobs.internal_config_provider import InternalConfigProviders
from api.bots.tr.good_queue_place import GoodQueuePlace


class GoodQueuePlaceWithQueueEnding(GoodQueuePlace):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, config_prov)
