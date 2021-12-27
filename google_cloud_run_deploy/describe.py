from .utils import generate_cloud_run_names, run_shell_command


def describe(deployment_name, deployment_spec, return_json=False):
    service_name, _ = generate_cloud_run_names(deployment_name)

    describe_command = [
        "gcloud",
        "run",
        "services",
        "describe",
        service_name,
        "--platform",
        str(deployment_spec["platform"]),
        "--region",
        str(deployment_spec["region"]),
        "--project",
        str(deployment_spec["project_id"]),
    ]

    if return_json:
        describe_command.append("--format=json")
    service_description, _ = run_shell_command(describe_command)

    if return_json:
        return service_description
    else:
        print(service_description)
