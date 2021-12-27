<div align="center">
    <h1>Google Cloud Run Operator</h1>
    <p>
        <img src="https://user-images.githubusercontent.com/5261489/147468164-c542e1a5-7fc0-4ec2-9000-d9dc446d4fe7.png" width=20%/>
    <p>
</div>

Cloud Run is Google Cloud's serverless solution for containers. With Cloud Run you can develop and deploy highly scalable containerized applications on a fully managed serverless platform. Cloud Run is great for running small to medium models since you only pay for the compute you use and it is super scalable.

This tool can be used as an Operator for [bentoctl](https://github.com/bentoml/bentoctl). See steps on how to add Cloud Run Deployment Tool as an operator [here](#deploy-to-cloud-run-with-bentoctl).

With the combination of [BentoML](https://github.com/bentoml/BentoML) and [bentoctl](https://github.com/bentoml/bentoctl), you can enjoy the flexibility of Cloud Run with any of the popular frameworks.

## Prerequisits

- Google cloud CLI tool
  - Install instruction: https://cloud.google.com/sdk/docs/install and make sure all your `gcloud` components are up to date. Run `gcloud components update` to update
  - Create a project and update `cloud_run_config.json` with your `project_id`
- Docker is installed and running on the machine
  - Install instruction: https://docs.docker.com/install
- Installed the required python packages
  ```bash
  $ pip install -r requirements.txt
  ```
- Build bento
  - Checkout [BentoML quickstart guide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb) for how to get it started


## Deploy to Cloud Run with bentoctl

1. Install bentoctl
    ```bash
    $ pip install bentoctl
    ```

2. Add Google Cloud Run operator
    ```bash
    $ bentoctl operator add google-cloud-run      
    Added google-cloud-run!                                              
    ```

3. Deploy to Heroku using bentoctl deploy command
    ```bash
    # Use the interactive mode
    $ bentoctl deploy 

    Bentoctl Interactive Deployment Spec Builder

    Welcome! You are now in interactive mode.

    This mode will help you setup the deployment_spec.yaml file required for
    deployment. Fill out the appropriate values for the fields.

    (deployment spec will be saved to: ./deployment_spec.yaml)

    api_version: v1
    metadata: 
        name: test-script
        operator: google-cloud-run
    spec: 
        bento: $BENTO_BUNDLE_PATH
        project_id: bentoml-43434
        region: us-central1
        port: 5000
        min_instances: 0
        max_instances: 1
        memory: 512Mi
        cpu: 1
        allow_unauthenticated: True
        platform: managed
    deployment spec file exists! Should I override? [Y/n]: Y
    deployment spec generated to: deployment_spec.yaml
    ~ Builing and Pushing Image
    ~ Deploying Image
    Successful deployment!

4. Get deployment information
    ```bash
    $ bentoctl describe deployment_spec.yaml

    ✔ Service test-script in region us-central1
 
    URL:     https://test-script-7zfol4b6tq-uc.a.run.app
    Ingress: all
    Traffic:
      100% LATEST (currently test-script-00001-vuq)
    
    Last updated on 2021-11-26T19:14:19.418723Z by your-email@gmail.com:
      Revision test-script-00001-vuq
      Image:         gcr.io/bentoml-43434/irisclassifier:20210923152106_c95f2e
      Port:          5000
      Memory:        512Mi
      CPU:           1
      Concurrency:   80
      Max Instances: 1
      Timeout:       300s
    ```

5. Make sample request
    ```bash
    $ curl -i \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[[5.1, 3.5, 1.4, 0.2]]' \
      https://test-script-7zfol4b6tq-uc.a.run.app/predict


    # Output
    HTTP/2 200 
    content-type: application/json
    x-request-id: fbe04e47-78ea-4520-8b39-e38a72d7628c
    x-cloud-trace-context: 131c57979f2808d5dc57ae7360d44ecd;o=1
    date: Fri, 26 Nov 2021 19:21:02 GMT
    server: Google Frontend
    content-length: 3
    alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43
    
    [0]
    ```

6. Delete deployment with BentoCTL
    ```bash
    $ bentoctl delete deployment_spec.yaml
    ```
## Configuring the Deployment
There is an optional config file available that you can use to specifiy the configs for you deployment, [cloud_run_config.json](cloud_run_config.json). 

This is the list of configurations you can use to deploy your bento to Google Cloud Run. Please refer to the documentation attached to each point for more information about the options.

The required configuration is: 
- `project_id`: You project id. This will be a unique id for each of your projects, specifying unique resources available to each project. If you haven't created a project, head over to the console and create it
  - check projects you already have by running `gcloud config get-value project`
- `region`: The region to which you want to deploy your Cloud Run service. Check
  the [official list](https://cloud.google.com/run/docs/locations) to know more
  about all the regions available
- `port`: The port that Cloud Run container should listen to. Note: this should be the same as the port that the bento service is listening to (by default 5000)
- `min-instances`: The number of minimum instances that Cloud Run should keep active. Check the [docs](https://cloud.google.com/run/docs/configuring/min-instances)for more info
- `max_instances`: The maximum number of instances Cloud Run should scale upto under load. Check the [dcos](https://cloud.google.com/run/docs/configuring/max-instances) on how to configure it
- `memory`: The RAM that should be available for each instance. If your model uses more than the specified RAM, it will be terminated. Check the [docs](https://cloud.google.com/run/docs/configuring/memory-limits)
- `cpu`: The number of CPUs needed for each instance. Check the [docs](https://cloud.google.com/run/docs/configuring/cpu) for more info
- `allow_unauthenticated`: Specify if the endpoint should receive request from the public. Check the [docs](https://cloud.google.com/run/docs/authenticating/public?hl=en)
- `platform`: The target platform for running the commands. Currently only
  `managed` is supported. Check out the [docs](https://cloud.google.com/sdk/gcloud/reference/run/deploy#--platform) to know more
  
## Deployment Command Reference

### Create a Deployment

Use command line
```bash
$ ./deploy <BENTO_BUNDLE_PATH> <DEPLOYMENT_NAME> <CONFIG_JSON, default is cloud_run_config.json>
```

```bash
BENTO_BUNDLE_PATH=${bentoml get IrisClassifier:latest --print-location -q)
$ ./deploy $BENTO_BUNDLE_PATH my_first_deployment cloud_run_config.json
```

Using Python API
```python
from google_cloud_run_deploy import deploy

deploy(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CLOUD_RUN_CONFIG)
```
* where `CLOUD_RUN_CONFIG` is a dictionary with keys for `"project_id"`, `"region"`, etc. More [here](#configuring-the-deployment)

### Update a Deployment

Use command line
```bash
$ ./update <BENTO_BUNDLE_PATH> <DEPLOYMENT_NAME> <CONFIG_JSON, default is cloud_run_config.json>
```

Use Python API
```python
from google_cloud_run_deploy import update

update(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CLOUD_RUN_CONFIG)
```
* where `CLOUD_RUN_CONFIG` is a dictionary with keys for `"project_id"`, `"region"`, etc. More [here](#configuring-the-deployment)

### Get a Deployment’s Status and Information

Use command line
```bash
$ ./describe <DEPLOYMENT_NAME>
```

Use Python API
```python
from google_cloud_run_deploy import describe

describe(DEPLOYMENT_NAME, CLOUD_RUN_CONFIG)
```
* where `CLOUD_RUN_CONFIG` is a dictionary with keys for `"project_id"`, `"platform"`, and `"region"`

### Delete a Deployment

Use command line
```bash
$ ./delete <DEPLOYMENT_NAME>
```

Use Python API
```python
from google_cloud_run_deploy import delete

delete(DEPLOYMENT_NAME, CLOUD_RUN_CONFIG)
```
* where `CLOUD_RUN_CONFIG` is a dictionary with keys for `"region"` and `"project_id"`
