# habr-app-demo

App demo for the [original Habr article](https://habr.com/ru/post/444446/).

For demo for the [second article about search](https://habr.com/ru/company/joom/blog/526550/), checkout `feature/search` branch.

## Running

    docker-compose up
    docker-compose exec backend python -m tools.add_test_content

Demo page should be available at [http://localhost:40002/card/helloworld](http://localhost:40002/card/helloworld).
