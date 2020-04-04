from backend.wiring import Wiring

if __name__ == "__main__":
    wiring = Wiring()
    wiring.task_manager.enqueue_building_cards_index()
