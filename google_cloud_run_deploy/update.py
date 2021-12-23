from .deploy import deploy


def update(bento_path, deployment_name, deployment_spec):
    # google cloud run is updated through deploying with the same config as the original
    deploy(bento_path, deployment_name, deployment_spec)
