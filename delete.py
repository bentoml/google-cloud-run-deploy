import os

import argparse

from describe import describe_cloud_run
from utils import run_shell_command, generate_cloud_run_names,console


def delete_cloud_run(deployment_name):
    service_name, _ = generate_cloud_run_names(deployment_name)

    service_data = describe_cloud_run(service_name, return_json=True)
    img = service_data["spec"]["template"]["spec"]["containers"][0]["image"]
    repo_name = img.split(":")[0]
    console.print(repo_name, deployment_name)

    console.print(f"Deleting Cloud Run service [{service_name}]")
    run_shell_command(["gcloud", "run", "services", "delete", service_name, "--quiet"])

    # get all images in container registry
    images, _ = run_shell_command(
        ["gcloud", "container", "images", "list-tags", repo_name, "--format=json"],
    )

    # loop through all the images in the container registry and delete them.
    with console.status(f"Deleting {args.deployment_name}"):
        for i, img in enumerate(images):
            print(f"\rDeleting image {i+1}/{len(images)}", end="")
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


if __name__ == "__main__":
    parser=argparse.ArgumentParser(
        description="Delete the bundle deployment on GCP",
        epilog="Check out https://github.com/bentoml/google-cloud-run-deploy#readme to know more"
    )
    parser.add_argument(
        "deployment_name",help="The name of the deployment you want to delete"
    )
    args=parser.parse_args()

    delete_cloud_run(args.deployment_name)
    console.print(f"[bold green]Deleted {args.deployment_name}!")