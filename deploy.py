import sys

from bentoml.saved_bundle import load_bento_service_metadata

from utils import run_shell_command, get_configuration_value, generate_cloud_run_names


def deploy_gcloud_run(bento_bundle_path, deployment_name, config_json):
    bundle_metadata = load_bento_service_metadata(bento_bundle_path)
    cloud_run_config = get_configuration_value(config_json)

    service_name, gcr_tag = generate_cloud_run_names(
        deployment_name,
        cloud_run_config["project_id"],
        bundle_metadata.name,
        bundle_metadata.version,
    )
    print(service_name, gcr_tag)

    img_name = gcr_tag.split("/")[-1]
    print(f"Building and Pushing {img_name}")
    run_shell_command(
        ["gcloud", "builds", "submit", bento_bundle_path, "--tag", gcr_tag]
    )

    print(f"Deploying [{img_name}] to Cloud Run Service [{service_name}]")
    port = str(cloud_run_config.get("port", 5000))
    run_shell_command(
        [
            "gcloud",
            "run",
            "deploy",
            service_name,
            "--image",
            gcr_tag,
            "--port",
            port,
            "--allow-unauthenticated",
        ]
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception(
            "Please provide bundle path, deployment name and path to Cloud Run "
            "config file (optional)"
        )
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "cloud_run_config.json"

    deploy_gcloud_run(bento_bundle_path, deployment_name, config_json)
