import json
import yaml
from app.main import app
from fastapi.openapi.utils import get_openapi

openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version=app.openapi_version,
    description=app.description,
    routes=app.routes,
)

with open("../docs/api/openapi.yaml", "w") as f:
    yaml.dump(openapi_schema, f, sort_keys=False)