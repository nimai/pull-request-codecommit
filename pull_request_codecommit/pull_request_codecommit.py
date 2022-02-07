from typing import Tuple, Optional

from .repository import Repository
from .aws import Client as AwsClient


class PullRequestCodeCommit:
    """
    Understands CodeCommit Pull requests
    """

    def __init__(self, repository: Repository) -> None:
        self.__aws_client: Optional[AwsClient] = None
        self.__repo = repository
        self.__data: dict = {}

    @property
    def __client(self) -> AwsClient:
        if not self.__aws_client:
            self.__aws_client = AwsClient(
                profile=self.__repo.remote.profile, region=self.__repo.remote.region
            )

        return self.__aws_client

    @property
    def pull_request_id(self) -> int:
        return self.__data.get("pullRequestId", 0)

    @property
    def description(self) -> str:
        return self.__data.get("description", "").replace("\n\n", "\n")

    @property
    def link(self) -> str:
        return self.__repo.remote.pull_request_url(self.pull_request_id)

    def save(self, title: str, description: str):
        self.__data = self.__create(
            title=title, description=self.__markdown_conversion(description)
        )

    def merge(self) -> str:
        response = self.__client.merge_pull_request(
            repository=self.__repo.remote.name,
            pull_request_id=self.pull_request_id,
        )
        status = response.get("pullRequestStatus", "")

        if status == "CLOSED":
            self.__repo.checkout_destination()

        return status

    @staticmethod
    def __markdown_conversion(description: str) -> str:
        return description.replace("\n", "\n\n")

    def __create(self, title: str, description: str) -> dict:
        return self.__client.create_pull_request(
            title=title,
            description=description,
            repository=self.__repo.remote.name,
            source=self.__repo.branch,
            destination=self.__repo.destination,
        )
