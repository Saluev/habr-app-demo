# habr-app-demo

App demo for [Habr article](https://habr.com/ru/post/444446/).

## Running

    docker-compose up
    docker-compose exec backend python -m tools.add_test_content
    docker-compose exec backend python -m tools.build_index

Demo page should be available at [http://localhost:40002/card/helloworld](http://localhost:40002/card/helloworld).
