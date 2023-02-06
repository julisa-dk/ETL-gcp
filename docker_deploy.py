from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer
from prefect.filesystems import GitHub
from etl_github import etl_parent_flow

docker_block = DockerContainer.load("zoom")
github_block = GitHub.load("github-block")

docker_dep = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name='docker-flow',
    infrastructure=docker_block
)

if __name__=="__main__":
    docker_dep.apply()

    

