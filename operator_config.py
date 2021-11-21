OPERATOR_NAME = "gcp-cloud-run"

OPERATOR_MODULE = "google_cloud_run_deploy"

OPERATOR_SCHEMA = {
    "project_id": {
        "required": True,
        "type": "string",
        "help_message": "project_id of the project that holds this deployment",
    },
    "region": {
        "required": True,
        "type": "string",
        "help_message": "The GCP region to which you want to deploy the service to",
    },
    "port": {
        "required": True,
        "type": "integer",
        "coerce": int,
        "default": 5000,
        "help_message": "The port to which you will send API requests",
    },
    "min_instances": {
        "required": True,
        "type": "integer",
        "coerce": int,
        "default": 0,
        "help_message": "Minimum number of instances the deployment should scale",
    },
    "max_instances": {
        "required": True,
        "type": "integer",
        "coerce": int,
        "default": 1,
        "help_message": "Maximum number of instances the deployment should scale",
    },
    "memory": {
        "required": True,
        "default": "512Mi",
    },
    "cpu": {
        "required": True,
        "default": 1,
    },
    "allow_unauthenticated": {
        "required": True,
        "default": True,
    },
    "platform": {
        "required": True,
        "default": "managed",
    }

}