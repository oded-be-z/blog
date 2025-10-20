"""
Git Worktree Manager
Follows best practices from SKILL_git_worktrees.md and GIT_WORKTREE_GUIDE.md
"""

import subprocess
import os
from datetime import date
from typing import List, Dict
from loguru import logger

class GitWorktreeManager:
    """Manages git worktrees for parallel article generation"""

    def __init__(self, repo_path: str = "/home/odedbe/blog"):
        self.repo_path = repo_path
        self.worktrees: Dict[str, str] = {}

    def create_worktrees(self, categories: List[str], date_str: str) -> Dict[str, str]:
        """
        Create git worktrees for parallel agent work

        Args:
            categories: List of categories (forex, crypto, commodities)
            date_str: Date string (YYYY-MM-DD)

        Returns:
            Dict mapping category to worktree path
        """
        logger.info(f"Creating worktrees for {len(categories)} categories")

        for category in categories:
            worktree_path = f"/home/odedbe/blog-{category}"
            branch_name = f"daily/{category}-{date_str}"

            try:
                # Create worktree with new branch
                cmd = [
                    "git", "worktree", "add",
                    worktree_path,
                    "-b", branch_name
                ]

                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )

                self.worktrees[category] = worktree_path
                logger.success(f"Created worktree for {category} at {worktree_path}")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to create worktree for {category}: {e.stderr}")
                raise

        return self.worktrees

    def merge_branches(self, branches: List[str]) -> bool:
        """
        Merge all agent branches into main

        Args:
            branches: List of branch names to merge

        Returns:
            True if all merges successful
        """
        logger.info(f"Merging {len(branches)} branches into main")

        try:
            # Ensure we're on main branch
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )

            # Merge each branch
            for branch in branches:
                logger.info(f"Merging branch: {branch}")
                result = subprocess.run(
                    ["git", "merge", branch, "--no-edit"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.success(f"Merged {branch}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Merge failed: {e.stderr}")
            return False

    def cleanup_worktrees(self, categories: List[str]) -> None:
        """
        Remove worktrees and delete branches after successful merge

        Args:
            categories: List of categories to clean up
        """
        logger.info(f"Cleaning up {len(categories)} worktrees")

        for category in categories:
            worktree_path = f"/home/odedbe/blog-{category}"

            try:
                # Remove worktree
                subprocess.run(
                    ["git", "worktree", "remove", worktree_path],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
                logger.success(f"Removed worktree: {worktree_path}")

            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to remove worktree {worktree_path}: {e.stderr}")

    def delete_branches(self, branches: List[str]) -> None:
        """
        Delete merged branches

        Args:
            branches: List of branch names to delete
        """
        logger.info(f"Deleting {len(branches)} merged branches")

        for branch in branches:
            try:
                subprocess.run(
                    ["git", "branch", "-d", branch],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
                logger.success(f"Deleted branch: {branch}")

            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to delete branch {branch}: {e.stderr}")

    def get_worktree_status(self) -> List[Dict]:
        """Get status of all worktrees"""
        try:
            result = subprocess.run(
                ["git", "worktree", "list"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split("\n")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get worktree status: {e.stderr}")
            return []
