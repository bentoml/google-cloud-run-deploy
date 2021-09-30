import os

import argparse

from ruamel.yaml import YAML

from utils import generate_cloud_run_names, run_shell_command


def describe_cloud_run(deployment_name,  config_json, return_json=False):
    service_name, _ = generate_cloud_run_names(deployment_name)

    if not return_json:
        stdout, stderr = run_shell_command(
            ["gcloud", "run", "services", "describe", service_name,
            "--platform", str(config_json["platform"]),
            "--region", str(config_json["region"])]
        )
        print(stdout)
    else:
        stdout, stderr = run_shell_command(
            ["gcloud", "run", "services", "describe", service_name, 
             "--platform", str(config_json["platform"]),
             "--region", str(config_json["region"]),
             "--format=export"]
        )
        yaml = YAML()
        data = yaml.load(stdout)

        return data


if __name__ == "__main__":
    parser=argparse.ArgumentParser(
        description="Describe the bundle deployed on GCP",
        epilog="Check out https://github.com/bentoml/google-cloud-run-deploy#readme to know more"
    )
    parser.add_argument("deployment_name", help="The name you want to use for your deployment")
    parser.add_argument(
        "config_json",
        help="(optional) The config file for your deployment",
        default=os.path.join(os.getcwd(), "cloud_run_config.json"),
        nargs="?",
    )
    args=parser.parse_args()

    describe_cloud_run(args.deployment_name,args.config_json)
    