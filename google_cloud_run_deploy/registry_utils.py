import json
import subprocess

USERNAME = "oauth2accesstoken"
GCR_DOMAIN = "gcr.io/{project_id}/{repository_name}"


def run_shell_command(command, cwd=None, env=None, shell_mode=False):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell_mode,
        cwd=cwd,
        env=env,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        try:
            return json.loads(stdout.decode("utf-8")), stderr.decode("utf-8")
        except json.JSONDecodeError:
            return stdout.decode("utf-8"), stderr.decode("utf-8")
    else:
        raise Exception(
            f'Failed to run command {" ".join(command)}: {stderr.decode("utf-8")}'
        )


def create_repository(deployment_name, operator_spec):
    """
    Create GCR repository and return the information.
    """

    repository_url = GCR_DOMAIN.format(
        project_id=operator_spec["project_id"], repository_name=deployment_name
    )
    access_code, _ = run_shell_command(
        ["gcloud", "auth", "print-access-token", "--quiet"]
    )

    return repository_url, USERNAME, access_code.strip()


def delete_repository(deployment_name, operator_spec):
    """
    Delete the GCR repository created
    """
    # get all images in container registry
    repository_url = GCR_DOMAIN.format(
        project_id=operator_spec["project_id"], repository_name=deployment_name
    )
    images, _ = run_shell_command(
        [
            "gcloud",
            "container",
            "images",
            "list-tags",
            repository_url,
            "--format=json",
        ],
    )

    # loop through all the images in the container registry and delete them.
    for i, img in enumerate(images):
        print(f"Deleting image {i+1}/{len(images)}")
        run_shell_command(
            [
                "gcloud",
                "container",
                "images",
                "delete",
                f"{repository_url}@{img['digest']}",
                "--force-delete-tags",
                "--quiet",
            ]
        )
    print(f"{deployment_name} repository deleted from gcr.io")
