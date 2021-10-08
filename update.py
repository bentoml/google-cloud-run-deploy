import os
import argparse

from describe import describe
from deploy import deploy
from utils import console


def update(bento_bundle_path, deployment_name, config_json):
    # the is just to standarise api
    # in google cloud run init deployment and updation are through `deploy()`
    deploy(bento_bundle_path, deployment_name, config_json)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the bentoml bundle on Google Cloud Run",
        epilog="Check out https://github.com/bentoml/google-cloud-run-deploy#readme to know more",
    )
    parser.add_argument(
        "deployment_name", help="The name you want to use for your deployment"
    )
    parser.add_argument(
        "config_json",
        help="(optional) The config file for your deployment",
        default=os.path.join(os.getcwd(), "cloud_run_config.json"),
        nargs="?",
    )
    args = parser.parse_args()

    update(args.bento_bundle_path, args.deployment_name, args.config_json)
    # show endpoint URL and other info
    console.print("[bold green]Updation Successful!")
    describe(args.deployment_name, args.config_json)
