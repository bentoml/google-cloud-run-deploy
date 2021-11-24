from .describe import describe
from .utils import console, generate_cloud_run_names, run_shell_command, get_metadata


def deploy(bento_bundle_path, deployment_name, cloud_run_config):
    bundle_metadata = get_metadata(bento_bundle_path)

    service_name, gcr_tag = generate_cloud_run_names(
        deployment_name,
        cloud_run_config["project_id"],
        bundle_metadata.get("name"),
        bundle_metadata.get("version"),
    )

    with console.status("Building and Pushing image"):
        run_shell_command(
            [
                "gcloud",
                "builds",
                "submit",
                bento_bundle_path,
                "--tag",
                gcr_tag,
                "--project",
                cloud_run_config["project_id"],
            ]
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
                "--project",
                str(cloud_run_config["project_id"]),
                "--allow-unauthenticated"
                if cloud_run_config["allow_unauthenticated"]
                else "--no-allow-unauthenticated",
            ]
        )
