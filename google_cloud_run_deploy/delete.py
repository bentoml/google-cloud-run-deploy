from .describe import describe
from .utils import (
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
                "--project",
                str(cloud_run_config["project_id"]),
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