import os
import argparse

from describe import describe
from utils import (
    run_shell_command,
    generate_cloud_run_names,
    get_configuration_value,
    console,
)


def delete(deployment_name, config_json):
    service_name, _ = generate_cloud_run_names(deployment_name)
    cloud_run_config = get_configuration_value(config_json)

    service_data = describe(service_name, config_json, return_json=True)
    img = service_data["spec"]["template"]["spec"]["containers"][0]["image"]
    repo_name = img.split(":")[0]

    with console.status(f"Deleting [[b]{service_name}[/b]]"):
        run_shell_command(
            [
                "gcloud",
                "run",
                "services",
                "delete",
                service_name,
                "--region",
                cloud_run_config["region"],
                "--quiet",
            ]
        )
    console.print(f"Deleted Cloud Run service [[b]{service_name}[/b]]")

    # get all images in container registry
    images, _ = run_shell_command(
        ["gcloud", "container", "images", "list-tags", repo_name, "--format=json"],
    )

    # loop through all the images in the container registry and delete them.
    for i, img in enumerate(images):
        with console.status(f"Deleting image {i+1}/{len(images)}"):
            run_shell_command(
                [
                    "gcloud",
                    "container",
                    "images",
                    "delete",
                    f"{repo_name}@{img['digest']}",
                    "--force-delete-tags",
                    "--quiet",
                ]
            )
    console.print("Deleted images")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete Google Cloud Run deployment",
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

    delete(args.deployment_name, args.config_json)
    console.print('[bold green]Deletion complete!')
