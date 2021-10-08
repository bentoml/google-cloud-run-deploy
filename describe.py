import os
import argparse

from utils import generate_cloud_run_names, run_shell_command, get_configuration_value


def describe(deployment_name, config_json, return_json=False):
    service_name, _ = generate_cloud_run_names(deployment_name)
    cloud_run_config = get_configuration_value(config_json)

    describe_command = [
        "gcloud",
        "run",
        "services",
        "describe",
        service_name,
        "--platform",
        str(cloud_run_config["platform"]),
        "--region",
        str(cloud_run_config["region"]),
        "--project",
        str(cloud_run_config["project_id"]),
    ]

    if return_json:
        describe_command.append("--format=json")
    service_description, _ = run_shell_command(describe_command)

    if return_json:
        return service_description
    else:
        print(service_description)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Describe the Google Cloud Run deployment.",
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

    describe(args.deployment_name, args.config_json)
