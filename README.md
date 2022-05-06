<div align="center">
    <h1>Google Cloud Run Operator</h1>
</div>

Cloud Run is Google Cloud's serverless solution for containers. With Cloud Run, you can develop and deploy highly scalable containerized applications on a fully managed serverless platform. Cloud Run is great for running small to medium models since you only pay for the compute you use and it is super scalable.

With the combination of [BentoML](https://github.com/bentoml/BentoML) and [bentoctl](https://github.com/bentoml/bentoctl), you can enjoy the flexibility of Cloud Run with your favourite ML frameworks and easily manage the infrastructure via terraform.

> **Note:** This operator is compatible with BentoML version 1.0.0 and above. For older versions, please switch to the branch `pre-v1.0` and follow the instructions in the README.md.


## Table of Contents

   * [Quickstart with bentoctl](#quickstart-with-bentoctl)
   * [Configuration Options](#configuration-options)

## Quickstart with bentoctl

This quickstart will walk you through deploying a bento into Google Cloud Run. Make sure to go through the [prerequisites](#prerequisites) section and follow the instructions to set everything up.

### Prerequisites

1. Google cloud CLI tool - Install instruction: https://cloud.google.com/sdk/docs/install and make sure all your `gcloud` components are up to date. Run `gcloud components update` to update
2. Terraform - Terraform is a tool for building, configuring, and managing infrastructure. Installation instruction: www.terraform.io/downloads
3. Docker - Install instruction: https://docs.docker.com/install
4. A working bento - for this guide, we will use the iris-classifier bento from the BentoML [quickstart guide](https://docs.bentoml.org/en/latest/quickstart.html#quickstart).


### Steps
1. Install bentoctl via pip
    ```bash
    pip install --pre bentoctl
    ```

2. Install AWS  operator

    Bentoctl will install the official Google Cloud Run operator and its dependencies.

    ```bash
    bentoctl operator install gcp-cloud-run
    ```

3. Initialize deployment with bentoctl

    Follow the interactive guide to initialize the deployment project.

    ```bash
    $ bentoctl init
    
    Bentoctl Interactive Deployment Config Builder

    Welcome! You are now in interactive mode.

    This mode will help you set up the deployment_config.yaml file required for
    deployment. Fill out the appropriate values for the fields.

    (deployment config will be saved to: ./deployment_config.yaml)

    api_version: v1
    name: quickstart
    operator: gcp-cloud-run
    template: terraform
    spec:
        project_id: bentoml-316710
        region: asia-east1
        port: 3000
        min_instances: 0
        max_instances: 1
        memory: 512M
        cpu: 1
    filename for deployment_config [deployment_config.yaml]:
    deployment config generated to: deployment_config.yaml
    ✨ generated template files.
      - ./main.tf
      - ./bentoctl.tfvars
    ```
    This will also run the `bentoctl generate` command for you and will generate the `main.tf` terraform file, which specifies the resources to be created and the `bentoctl.tfvars` file which contains the values for the variables used in the `main.tf` file.

4. Build and push docker image into Google Container Registry.

    ```bash
    bentoctl build -b iris_classifier:latest -f deployment_config.yaml
    ```
    The iris-classifier service is now built and pushed into the container registry and the required terraform files have been created. Now we can use terraform to perform the deployment.
    
5. Apply Deployment with Terraform

   1. Initialize terraform project. This installs the AWS provider and sets up the terraform folders.
        ```bash
        terraform init
        ```

   2. Apply terraform project to create Cloud Run deployment

        ```bash
        terraform apply -var-file=bentoctl.tfvars -auto-approve
        ```

6. Test deployed endpoint

    The `iris_classifier` uses the `/classify` endpoint for receiving requests so the full URL for the classifier will be in the form `{EndpointUrl}/classify`.

    ```bash
    URL=$(terraform output -json | jq -r .Endpoint.value)/classify
    curl -i \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[5.1, 3.5, 1.4, 0.2]' \
      $URL
    ```

7. Delete deployment
    Use the `bentoctl destroy` command to remove the registry and the deployment

    ```bash
    bentoctl destroy -f deployment_config.yaml
    ```
    
## Configuration Options

This is the list of configurations you can use to deploy your bento to Google Cloud Run. For more information about options check the corresponding Google Cloud Run docs provided.

The required configuration is: 
- `project_id`: Your project id. This will be a unique id for each of your projects, specifying unique resources available to each project. If you haven't created a project, head over to the console and create it
  - check projects you already have by running `gcloud config get-value project`
- `region`: The region to which you want to deploy your Cloud Run service. Check
  the [official list](https://cloud.google.com/run/docs/locations) to know more
  about all the regions available
- `port`: The port that Cloud Run container should listen to. Note: this should be the same as the port that the bento service is listening to (by default 5000)
- `min-instances`: The number of minimum instances that Cloud Run should keep active. Check the [docs](https://cloud.google.com/run/docs/configuring/min-instances)for more info
- `max_instances`: The maximum number of instances Cloud Run should scale up to under load. Check the [dcos](https://cloud.google.com/run/docs/configuring/max-instances) on how to configure it
- `memory`: The RAM that should be available for each instance. If your model uses more than the specified RAM, it will be terminated. Check the [docs](https://cloud.google.com/run/docs/configuring/memory-limits)
- `cpu`: The number of CPUs needed for each instance. Check the [docs](https://cloud.google.com/run/docs/configuring/cpu) for more info
