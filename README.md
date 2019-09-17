# Deviget Challenge

## 1. Introduction
This repository contains a Python/Falcon application that implements a REST API for a
[Minesweeper](https://en.wikipedia.org/wiki/Minesweeper_(video_game)) game.

This development was encouraged by the [challenge](https://github.com/deviget/minesweeper-API)
proposed to me by the [Deviget](https://www.deviget.com) Company in the context of a job interview.


## 2. Requirements

### 2.1 Hardware Requirementes
The application was developed and tested in a computer with the following hardware specs:
- Debian GNU/Linux 9 (stretch)
- 4 CPU cores
- 16 GB RAM

However, the application itself is lightweight enough to run in far more restricted hardware.
Any single core computer with at least 512 MB RAM will suffice for testing purposes.

### 2.2 Software Requirements
In order to be able to run the application you will need to have installed the following software packages:
  - [Python](https://www.python.org) (3.7 or higher)
  - [Pip](https://pypi.org/project/pip/)
  - [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/)
  - [Docker](https://www.docker.com) (19.03.2 or higher)
  - [Docker compose](https://docs.docker.com/compose/) (1.23.2 or higher)
  - A [MongoDB](https://www.mongodb.com) client of your preference
  ([mongo shell](https://docs.mongodb.com/manual/administration/install-community/),
  [Robo3t](https://robomongo.org), [Humong](https://www.humongous.io))

### 2.2.1 Python Dependencies
Also, the Python package containing the API relies on the following packages from the
[PyPy](https://pypi.org/project/dnspython/) repository:
- [pyyaml](https://pypi.org/project/PyYAML/)
- [falcon](https://pypi.org/project/falcon/)
- [marshmallow](https://pypi.org/project/marshmallow/)
- [gunicorn](https://pypi.org/project/gunicorn/)
- [bcrypt](https://pypi.org/project/bcrypt/)
- [cryptography](https://pypi.org/project/cryptography/)
- [pyjwt](https://pypi.org/project/PyJWT/)
- [mongoengine](https://pypi.org/project/mongoengine/)
- [blinker](https://pypi.org/project/blinker/)
- [dnspython](https://pypi.org/project/dnspython/)


## 3. Deployment

### 3.1 Local Deployment
In order to run a working copy of the application, you will need to follow these steps:

1. Clone this repository
```
$ git clone https://github.com/cdipietro/deviget.git
$ cd deviget
```

2. Build the docker image for the Python application:
```
$ docker build -t minesweeper/api .
```

3. Generate 3 secure passwords by running the following command 3 times:
```
$ docker-compose run --rm minesweeper_api python -c 'from minesweeper.common.auth import generate_secret_key ; print(generate_secret_key())'
```

4. Create a copy of the configuration file template and edit it to adjusts each of the configuration parameters with the desired values:
```
$ cp minesweeper/config/config-sample.yml minesweeper/config/config.yml
$ nano minesweeper
```
While editing the file, please make sure to:
  - Set up your `database:host` as `local.mongo`
  - Use 1st previously generated passwords as your `app:auth:pwd_key_secret`
  - Use 2nd previously generated passwords as your `app:auth:api_key_secret`
  - Use 3rd previously generated passwords as your `database:password` and make sure to copy database credentials into
  `docker-compose.yml` `MONGO_INITDB_*` environment variables.

5. Deploy the application along with its database by creating a `docker-compose` stack:
```
$ docker-compose up -d
```

6. Once the stack is up and running, you can check the API logs by running:
```
$ docker-compose logs -f minesweeper_api
```

### 3.2 Cloud Test Environment
In case you don't want to carry with the burden of deploying things locally, you can rely on the
environment of the API that I have deployed on the cloud for testing purposes.

This environment relies in [Heroku](https://www.heroku.com/) service for hosting the application API and
in [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) service for hosting the application database.
You can access the API anytime at https://deviget-minesweeper-cdipietro.herokuapp.com.

Moreover, I also created a [Postman Collection](https://documenter.getpostman.com/view/4944534/SVmtyKyB?version=latest)
with a set of examples on how to use and interact with the API.

You can use this collection either for sending the requests it contains to the API or either as an example for creating
your own requests. For convenience, this collection has already been configured (through a Postman Environment) with
a set of variables that aims any request towards the Heroku environment.


## 4. Use
Once you have deployed the application you can play the game as follows:
(In case you decide to use the cloud test environment, simply replace the `localhost:8000`
portion of the URL with https://deviget-minesweeper-cdipietro.herokuapp.com)

1. Create a user by issuing a POST request to the `localhost:8000/user`
```
curl --location --request POST "localhost:8000/user" \
  --header "Content-Type: application/json" \
  --data "{
    \"name_last\": \"Doe\",
    \"name_first\": \"John\",
    \"email\": \"john.doe@test.com\",
    \"password\": \"unsecure-password-1234\"
}"
```
Make sure to take note of the user `id` in the response, as you will need it for later requests

2. Create a game by issuing a POST request to the `localhost:8000/game`
```
curl --location --request POST "localhost:8000/game" \
  --header "Content-Type: application/json" \
  --data "{
    \"player_id\": \"{{user_id}}\",
    \"board\": {
        \"nbr_rows\": 5,
        \"nbr_columns\": 5,
        \"nbr_mines\": 5
    }
}
"
```
Make sure to take note of the game `id` in the response, as you will need it for later requests.

3. Start your newly created game by issuing a POST request to the `localhost:8000/game/<game_id>/start`
```
curl --location --request POST "localhost:8000/start" --header "Content-Type: application/json"
```

4. Check how the game elapsed time increases by issuing a GET request to the `localhost:8000/game/<game_id>`
```
curl --location --request GET "localhost:8000/game/{{game_id}}"
```

5. Pause or resume the game any time by issuing a POST request to the `localhost:8000/game/<game_id>/pause`
```
curl --location --request POST "localhost:8000/game/{{game_id}}/pause" \
--header "Content-Type: application/json"
```

6. Flag or unflag any board cell by issuing a POST request to the `localhost:8000/game/<game_id>/flag`
```
curl --location --request POST "localhost:8000/game/{{game_id}}/flag" \
  --header "Content-Type: application/json" \
  --data "{
    \"row\": 1,
    \"column\": 4
}"
```

7. Open any board cell by issuing a POST request to the `localhost:8000/game/<game_id>/open`
```
curl --location --request POST "localhost:8000/game/{{game_id}}/open" \
  --header "Content-Type: application/json" \
  --data "{
    \"row\": 1,
    \"column\": 4
}"
```

8. You will be able to perform 5, 6 and 7 as long as you don't win or lose the game. You can
check the status of a game at any time like you did on step 4.


## 5. Version
Current version is 0.1.0. Please take into account that this still is an alpha version.


## 6. Authors
This proyect was entirely developed by [Carlos A. Di Pietro](https://about.me/cdipietro).


## 7. Licence
This software is distributed under the [MIT License](https://cdipietro.mit-license.org).


## 8. Final Comments
This challenge was meant to be conducted in a time boxed manner, having only 2 days for completing it. Therefore,
there are many desirable functionalities that had to be left out of the scope challenge due to the time contraints.

Some of the many aspects to correct and improve in order to obtain a more reliable, robust and usable application are:

- Add users authentication and log-in endpoint
- Add permissions and authorization checks in all endpoints
- Sanitize input parameters from requests
- Paginate API responses
- Add more logging statements for debugging purposes
- Create unit-tests
- Write formal API documentation (possibly with [RAML](https://raml.org))
- Implement a webapp as GUI (possibly with [VUE.js](https://vuejs.org))

