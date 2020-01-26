from backend.search.indexer import Indexer
from backend.tasks.task import task


@task
def index(indexer: Indexer):
    new_index_name = indexer.build_new_cards_index()
    indexer.switch_current_cards_index(new_index_name)
