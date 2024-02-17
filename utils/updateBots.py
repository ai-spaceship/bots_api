import boto3
import time

cluster_name = "devCluster"
task_definition = "matrix_bot:5"
launch_type = "FARGATE"
network_configuration = {
    'awsvpcConfiguration': {
        'subnets': ['subnet-0ae819d09c7885683'],  # replace with your subnet id
        'assignPublicIp': 'DISABLED'  # or 'DISABLED' depending on your needs
    }
}


def update_agent_bots(region_name, cluster):
    ecs_client = boto3.client('ecs', region_name=region_name)
    get_task_id = ecs_client.list_tasks(cluster=cluster)
    print(get_task_id["taskArns"])
    get_tasks = ecs_client.describe_tasks(
        cluster=cluster, tasks=get_task_id["taskArns"])
    for i in get_task_id["taskArns"]:
        ecs_client.stop_task(cluster=cluster, task=i)
    time.sleep(5)
    for i in get_tasks["tasks"]:
        data = i["overrides"]['containerOverrides'][0]["environment"]
        response = ecs_client.run_task(
            cluster=cluster_name,
            taskDefinition=task_definition,
            launchType=launch_type,
            networkConfiguration=network_configuration,
            overrides={
                'containerOverrides': [{
                    'name': 'matrix_bot',  # Replace with the name of your container
                    'environment': data,
                }],
            },
        )

if __name__ == "__main__":
    update_agent_bots('us-east-1', 'devCluster')
