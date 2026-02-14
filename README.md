## Starting the containers ##
```bash
docker compose up -d
```

Adding sample data:
```bash
docker compose exec -it web python -m abcde.utils
```

OpenAPI docs
http://localhost:8080/docs


## Design considerations, limitations ##

### Query processing ###
Natural language parsing is not an straight forward task. LLMs can be used to extract the data, but running LLM in this scope was not an option.
Instead I implemented a technique similar to Named Entity Recognition - extract parts of the text using rules. This might not be a very robust solution.

The solution has the following features/limitations:
- supports temperature, humidity, rain and wind metric with similarity (typo, case insensitive) support. the supported values are hardcoded, no dynamic values from DB.
- supports min, max, sum and average aggreagtions with similarity (typo, case insensitive) support.
- supports multiple form of date instructions:
- - (last|previous|past) X (days|weeks|hours|minutes|seconds|months) with similarity (typo, case insensitive) support. eg.: last 7 days
- - (last|previous|past) (days|weeks|hours|minutes|seconds|months) with similarity (typo, case insensitive) support. eg.: previous month
- - since (date) with similarity (typo, case insensitive) support, multiple date format. it only supports dates (no time support). eg.: 2012.01.01
- sensor naming/support is limited - it is always sensorN without whitespace. the supported values are hardcoded, no dynamic values from DB.
- - sensor x. the "sensor" part supports similarity
- - sensorx. in this case it only supports exact match
- - all sensor. supports similarity


### Database ###
I've selected SQLite because of it's light weight, and also because no additional service was needed. In a real-word product some kind of time-series database would be preferrable.

Internally the database is stored in /tmp/database.db

### Architecture ###
I've used FastAPI as the framework because it's a realtively lightweight, modern and feature-rich framework. Also it comes with async support.

### Code quality ###
There is very limited docstring coverage on the classes/methods/functions. Also the language parse code and logic could be reworked to a more compact and possibly beter form. The test coverage is around 90%, only the critical parts are covered with a few tests.


## Tests ##
```bash
poetry run pytest
```
## Formatting ##
```bash
ruff check
ruff format
```

## Linting ##
```bash
pylint abcde
```

## Additional commands ##
```bash
poetry export --without-hashes --output requirements.txt
```
