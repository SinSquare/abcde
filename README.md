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
Instead I implemented a technique similar to Named Entity Recognition - extract parts of the text using rules. This is of course not a very robust solution.
As a general rule the first values will be used from the extracted values.

### Database ###
I've selected SQLite becuase of it's light weight, and also because no additional service was needed. Of course in a real-word product some kind of time-series database would be preferrable.

Internally the database is stored in /tmp/database.db

### Architecture ###
I've used FastAPI as the framework because it's a realtively lightweight, modern and feature-rich framework. Also it comes with async support.

### Code quality ###
There is very limited docstring coverage on the classes/methods/functions. Also the language parse code and logic could be reworked to a more compact and possibly beter form. The test coverage is around 94%, only the critical parts are covered with a few tests.


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
