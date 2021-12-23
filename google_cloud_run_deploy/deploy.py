from bentoml.bentos import containerize

from .describe import describe
from .utils import (
    console,
    generate_cloud_run_names,
    run_shell_command,
    get_tag_from_path,
    push_image
)


def deploy(bento_path, deployment_name, deployment_spec):
    bento_tag = get_tag_from_path(bento_path)

    service_name, gcr_tag = generate_cloud_run_names(
        deployment_name,
        deployment_spec["project_id"],
        bento_tag.name,
        bento_tag.version,
    )

    with console.status("Containerizing bento"):
        containerize(bento_tag.name, docker_image_tag=gcr_tag)

    with console.status('Pushing bento to gcr'):
        # docker login to gcr.io
        run_shell_command(["gcloud", "auth", "configure-docker", "gcr.io", "--quiet"])
        push_image(gcr_tag)

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
                str(deployment_spec.get("port")),
                "--memory",
                deployment_spec["memory"],
                "--cpu",
                str(deployment_spec["cpu"]),
                "--min-instances",
                str(deployment_spec["min_instances"]),
                "--max-instances",
                str(deployment_spec["max_instances"]),
                "--platform",
                str(deployment_spec["platform"]),
                "--region",
                str(deployment_spec["region"]),
                "--project",
                str(deployment_spec["project_id"]),
                "--allow-unauthenticated"
                if deployment_spec["allow_unauthenticated"]
                else "--no-allow-unauthenticated",
            ]
        )
