from .utils import generate_cloud_run_names, run_shell_command


def describe(deployment_name, cloud_run_config, return_json=False):
    service_name, _ = generate_cloud_run_names(deployment_name)

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
