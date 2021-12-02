from .deploy import deploy


def update(bento_bundle_path, deployment_name, config_json):
    # google cloud run is updated through deploying with the same config as the original
    deploy(bento_bundle_path, deployment_name, config_json)
