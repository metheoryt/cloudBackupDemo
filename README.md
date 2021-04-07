# Cloud backup utility

Archive and upload specified folder into every configured cloud provider

## Configuring

All configuration is done through:
- `.env` contains all necessary to specify options. All environment variables listed in `.env.dist`
- `config/providers.yml` contains info about all cloud providers. See template in `config/providers.dist.yml`
- `config/logging.yml` contains logging configuration. Basic config template see in `config/logging.dist.yml`

## Deploy & Run

To install dependencies, from project root:
```
$> pip install --upgrade pip
$> pip install --upgrade pipenv
$> pipenv sync
```

To launch application, hit
```
$> pipenv run uvicorn main:api --host=0.0.0.0 --port=8080 --log-config=config/logging.yml
```

> check `uvicorn --help` to see all options
