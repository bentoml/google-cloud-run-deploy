import argparse
import os

from bentoml.saved_bundle import load_bento_service_metadata

from describe import describe
from utils import (
    run_shell_command,
    get_configuration_value,
    generate_cloud_run_names,
    console,
)


def deploy(bento_bundle_path, deployment_name, config_json):
    bundle_metadata = load_bento_service_metadata(bento_bundle_path)
    cloud_run_config = get_configuration_value(config_json)

    service_name, gcr_tag = generate_cloud_run_names(
        deployment_name,
        cloud_run_config["project_id"],
        bundle_metadata.name,
        bundle_metadata.version,
    )

    with console.status("Building and Pushing image"):
        run_shell_command(
            ["gcloud", "builds", "submit", bento_bundle_path, "--tag", gcr_tag]
        )

    with console.status("Deploying to Cloud Run"):
        run_shell_command(
            [
                "gcloud",
                "run",
                "deploy",
                service_name,
                "--image",
                gcr_tag,
                "--port",
                str(cloud_run_config.get("port")),
                "--memory",
                cloud_run_config["memory"],
                "--cpu",
                str(cloud_run_config["cpu"]),
                "--min-instances",
                str(cloud_run_config["min_instances"]),
                "--max-instances",
                str(cloud_run_config["max_instances"]),
                "--platform",
                str(cloud_run_config["platform"]),
                "--region",
                str(cloud_run_config["region"]),
                "--allow-unauthenticated"
                if cloud_run_config["allow_unauthenticated"]
                else "--no-allow-unauthenticated",
            ]
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deploy the bentoml bundle on Google Cloud Run",
        epilog="Check out https://github.com/bentoml/google-cloud-run-deploy#readme to know more",
    )
    parser.add_argument("bento_bundle_path", help="Path to bentoml bundle")
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

    deploy(args.bento_bundle_path, args.deployment_name, args.config_json)
    console.print("[bold green]Deployment Successful!")
    # show details of the deployment
    describe(args.deployment_name, args.config_json)
