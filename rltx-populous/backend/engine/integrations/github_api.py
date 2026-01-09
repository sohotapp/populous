"""
GitHub API Integration

Provides REAL GitHub metrics for developer tools companies:
- Repository stars
- Contributor count
- Commit velocity
- Issue activity
- Fork count

This is a quick win for data quality - GitHub API is free and well-documented.
"""

import os
import httpx
from typing import Dict, Optional, Any, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio


class GitHubMetrics(BaseModel):
    """GitHub metrics for a company/project"""
    repo_name: str
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    contributors: int = 0
    commits_last_month: int = 0
    last_commit_date: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None

    # Derived metrics
    velocity_score: float = 0.0  # 0-1 based on activity
    community_score: float = 0.0  # 0-1 based on engagement

    # Data quality
    data_source: str = "github_api"
    fetched_at: str = ""


class GitHubAPI:
    """
    GitHub API client for fetching repository metrics.

    Works without authentication (60 req/hour) or with token (5000 req/hour).
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Populous-Decision-Intelligence"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def search_company_repos(self, company_name: str, limit: int = 5) -> List[Dict]:
        """
        Search for repositories belonging to a company.

        Tries multiple strategies:
        1. Search by organization name
        2. Search by repository name containing company
        3. Search by topic
        """
        repos = []

        async with httpx.AsyncClient() as client:
            # Strategy 1: Search org
            try:
                org_url = f"{self.BASE_URL}/orgs/{company_name.lower().replace(' ', '-')}/repos"
                response = await client.get(org_url, headers=self.headers, params={"per_page": limit, "sort": "stars"})
                if response.status_code == 200:
                    repos = response.json()
            except Exception:
                pass

            # Strategy 2: Search repos if org not found
            if not repos:
                try:
                    search_url = f"{self.BASE_URL}/search/repositories"
                    params = {
                        "q": f"{company_name} in:name,description",
                        "sort": "stars",
                        "order": "desc",
                        "per_page": limit
                    }
                    response = await client.get(search_url, headers=self.headers, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        repos = data.get("items", [])
                except Exception:
                    pass

        return repos

    async def get_repo_metrics(self, owner: str, repo: str) -> Optional[GitHubMetrics]:
        """
        Get detailed metrics for a specific repository.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Get basic repo info
                repo_url = f"{self.BASE_URL}/repos/{owner}/{repo}"
                response = await client.get(repo_url, headers=self.headers)

                if response.status_code != 200:
                    return None

                data = response.json()

                # Get contributors count
                contributors = 0
                try:
                    contrib_url = f"{self.BASE_URL}/repos/{owner}/{repo}/contributors"
                    contrib_response = await client.get(contrib_url, headers=self.headers, params={"per_page": 1})
                    if contrib_response.status_code == 200:
                        # Check Link header for total count
                        link_header = contrib_response.headers.get("Link", "")
                        if "last" in link_header:
                            # Parse last page number
                            import re
                            match = re.search(r'page=(\d+)>; rel="last"', link_header)
                            if match:
                                contributors = int(match.group(1))
                        else:
                            contributors = len(contrib_response.json())
                except Exception:
                    pass

                # Get recent commit activity
                commits_last_month = 0
                try:
                    since = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
                    commits_url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
                    commits_response = await client.get(
                        commits_url,
                        headers=self.headers,
                        params={"since": since, "per_page": 100}
                    )
                    if commits_response.status_code == 200:
                        commits_last_month = len(commits_response.json())
                except Exception:
                    pass

                # Calculate derived scores
                stars = data.get("stargazers_count", 0)
                forks = data.get("forks_count", 0)

                # Velocity score (based on commits and recency)
                velocity_score = min(1.0, commits_last_month / 50)  # 50 commits/month = 1.0

                # Community score (based on stars, forks, contributors)
                community_score = min(1.0, (
                    (stars / 10000) * 0.4 +
                    (forks / 1000) * 0.3 +
                    (contributors / 100) * 0.3
                ))

                return GitHubMetrics(
                    repo_name=f"{owner}/{repo}",
                    stars=stars,
                    forks=forks,
                    watchers=data.get("watchers_count", 0),
                    open_issues=data.get("open_issues_count", 0),
                    contributors=contributors,
                    commits_last_month=commits_last_month,
                    last_commit_date=data.get("pushed_at"),
                    language=data.get("language"),
                    description=data.get("description"),
                    created_at=data.get("created_at"),
                    velocity_score=velocity_score,
                    community_score=community_score,
                    fetched_at=datetime.now().isoformat()
                )

            except Exception as e:
                print(f"[GitHubAPI] Error fetching {owner}/{repo}: {e}")
                return None

    async def get_company_metrics(self, company_name: str) -> Optional[GitHubMetrics]:
        """
        Get aggregated GitHub metrics for a company.

        Finds the most relevant repository and returns its metrics.
        """
        repos = await self.search_company_repos(company_name, limit=3)

        if not repos:
            return None

        # Get metrics for the top repo (most stars)
        top_repo = repos[0]
        owner = top_repo.get("owner", {}).get("login", "")
        repo_name = top_repo.get("name", "")

        if not owner or not repo_name:
            return None

        return await self.get_repo_metrics(owner, repo_name)


# Singleton instance
_github_api: Optional[GitHubAPI] = None


def get_github_api() -> GitHubAPI:
    """Get or create GitHub API singleton"""
    global _github_api
    if _github_api is None:
        _github_api = GitHubAPI()
    return _github_api


async def fetch_github_metrics(company_name: str) -> Optional[GitHubMetrics]:
    """
    Convenience function to fetch GitHub metrics for a company.

    Usage:
        metrics = await fetch_github_metrics("Greptile")
        if metrics:
            print(f"Stars: {metrics.stars}")
    """
    api = get_github_api()
    return await api.get_company_metrics(company_name)
