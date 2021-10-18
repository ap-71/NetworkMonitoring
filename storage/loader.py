from observer import DefaultObserver
from storage.storage import IStorageFacade, StorageFacade, RAMMemoryStorage

storage: IStorageFacade = StorageFacade(storage=RAMMemoryStorage(), observer=DefaultObserver())
