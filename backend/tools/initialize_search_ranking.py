from backend.wiring import Wiring

if __name__ == "__main__":
    wiring = Wiring()
    wiring.search_ranking_manager.initialize_ranking()
