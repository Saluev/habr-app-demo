# habr-app-demo

App demo for [Habr article](https://habr.com/ru/post/444446/).

## Running

    docker-compose up
    docker-compose exec backend python -m tools.add_test_content
    docker-compose exec -T backend python -m tools.add_movies < ~/Downloads/tmdb-movie-metadata/tmdb_5000_movies.csv
    docker-compose exec backend python -m tools.build_index

Demo page should be available at [http://localhost:40002/card/helloworld](http://localhost:40002/card/helloworld).

## Setting up ranking

    docker-compose exec backend python -m tools.initialize_search_ranking

    # Generate events (replace with real events aggregation if you can!)
    docker-compose exec -T backend \
        python -m tools.generate_movie_events \
        < ~/Downloads/tmdb-movie-metadata/tmdb_5000_movies.csv \
        > ~/Downloads/habr-app-demo-dataset-events.csv

    # Compute features
    docker-compose exec -T backend \
        python -m tools.compute_features \
        < ~/Downloads/habr-app-demo-dataset-events.csv \
        > ~/Downloads/habr-app-demo-dataset-features.csv

    # Train model
    python backend/tools/train_search_ranking_model.py \
        --events ~/Downloads/habr-app-demo-dataset-events.csv \
        --features ~/Downloads/habr-app-demo-dataset-features.csv \
        -o ~/Downloads/habr-app-demo-model.json
    
    # Upload model
    docker-compose exec -T backend python -m tools.upload_search_ranking_model < ~/Downloads/habr-app-demo-model.json
