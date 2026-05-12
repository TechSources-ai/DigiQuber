import os
import boto3
import logging

logger = logging.getLogger(__name__)


def get_ssm_params(path="/digiquber/staging/", region="ap-south-2"):
    client = boto3.client("ssm", region_name=region)
    params = {}

    kwargs = {
        "Path": path,
        "Recursive": True,
        "WithDecryption": True,
    }

    try:
        while True:
            response = client.get_parameters_by_path(**kwargs)
            for p in response["Parameters"]:
                key = p["Name"].replace(path, "")
                params[key] = p["Value"]
            next_token = response.get("NextToken")
            if not next_token:
                break
            kwargs["NextToken"] = next_token

        logger.info("SSM: loaded %d parameters", len(params))

    except Exception as e:
        logger.exception("SSM fetch failed: %s", e)
        raise RuntimeError(f"Could not load config from SSM: {e}")

    return params


def load_config():
    # LOCAL DEV — use .env.staging file
    if os.environ.get("DJANGO_ENV") == "local":
        import environ
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent
        env = environ.Env()
        environ.Env.read_env(str(BASE_DIR / '.env.staging'))
        return dict(os.environ)

    # STAGING/PROD — use SSM
    return get_ssm_params()


SSM = load_config()