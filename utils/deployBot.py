import boto3

def start_ecs_task(env_vars, region_name='us-east-1'):
    """
    Start a task in an ECS cluster with overridden environment variables.

    Parameters:
    - cluster_name: The name of the ECS cluster.
    - task_definition: The family and revision (`family:revision`) or full ARN of the task definition to run.
    - launch_type: The launch type on which to run your task ('EC2' or 'FARGATE').
    - network_configuration: The network configuration for the task. This parameter is required for task definitions
      that use the 'awsvpc' network mode to receive their own elastic network interface.
    - env_vars: A dictionary containing the environment variables to override in the task.
    - region_name: The region where the ECS cluster is located. Defaults to 'us-east-1'.

    Returns:
    - response: The response from the ECS run_task request.
    """
    # Create a boto3 client for ECS
    ecs_client = boto3.client('ecs', region_name=region_name)

    # Format environment variables for ECS
    environment = [{'name': key, 'value': str(value)} for key, value in env_vars.items()]

    cluster_name = "devCluster"
    task_definition = "matrix_bot:4"
    launch_type = "FARGATE"
    network_configuration = {
        'awsvpcConfiguration': {
            'subnets': ['subnet-0ae819d09c7885683'],  # replace with your subnet id
            'assignPublicIp': 'DISABLED' # or 'DISABLED' depending on your needs
        }
    }

    # Override the environment variables in the container definition
    # Note: This assumes you have only one container in the task definition. 
    # If you have more, you'll need to adjust the 'containerOverrides' accordingly.
    response = ecs_client.run_task(
        cluster=cluster_name,
        taskDefinition=task_definition,
        launchType=launch_type,
        networkConfiguration=network_configuration,
        overrides={
            'containerOverrides': [{
                'name': 'matrix_bot', # Replace with the name of your container
                'environment': environment,
            }],
        },
    )
    return response

if __name__ == "__main__":
# Example usage:
    env_vars = {
        "HOMESERVER": "https://matrix.pixx.co",
        "USER_ID": "@example:pixx.co",
        "PASSWORD": "matrix bot password",
        "DEVICE_ID": "device_id",
        "SUPERAGENT_URL": "api.pixx.co",
        "AGENT_ID": "enter superagent agent id here",
        "API_KEY": "enter api key here",
        "type" : "AGENT" # "WORKFLOW"
    }

    # Call the function with the example parameters
    response = start_ecs_task(env_vars)
    print(response)
