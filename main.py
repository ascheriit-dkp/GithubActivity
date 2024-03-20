#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta
from random import randint
import subprocess
import sys

class GitRepository:
    def __init__(self, directory, user_name=None, user_email=None):
        self.directory = directory
        self.user_name = user_name
        self.user_email = user_email

    def initialize(self):
        os.makedirs(self.directory, exist_ok=True)
        os.chdir(self.directory)
        self.run_command(['git', 'init'])
        if self.user_name:
            self.run_command(['git', 'config', 'user.name', self.user_name])
        if self.user_email:
            self.run_command(['git', 'config', 'user.email', self.user_email])

    def run_command(self, command):
        subprocess.run(command, check=True)

    def commit(self, message, date):
        filename = "README.md"
        with open(filename, 'a') as file:
            file.write(f"{message}\n")
        self.run_command(['git', 'add', filename])
        self.run_command(['git', 'commit', '-m', message, '--date', date.strftime('%Y-%m-%d %H:%M:%S')])

def parse_arguments():
    parser = argparse.ArgumentParser(description="Automatically generate a Git repository with a customized commit history.")
    parser.add_argument("--no-weekends", action="store_true", help="Do not commit on weekends.")
    parser.add_argument("--max-commits", type=int, default=10, choices=range(1, 21), help="Maximum number of commits per day (1-20).")
    parser.add_argument("--frequency", type=int, default=80, help="Frequency of commit days (%).")
    parser.add_argument("--repository", help="URL of the remote repository.")
    parser.add_argument("--user-name", help="Git user name.")
    parser.add_argument("--user-email", help="Git user email.")
    parser.add_argument("--days-before", type=int, default=365, help="Start generating commits from N days before today.")
    parser.add_argument("--days-after", type=int, default=0, help="Continue generating commits until N days after today.")
    return parser.parse_args()

def generate_commit_dates(start_date, end_date, frequency, no_weekends, max_commits):
    commit_dates = []
    delta = end_date - start_date
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        if (not no_weekends or day.weekday() < 5) and randint(1, 100) <= frequency:
            for _ in range(randint(1, max_commits)):
                commit_dates.append(day)
    return commit_dates

def main():
    args = parse_arguments()

    start_date = datetime.now().replace(hour=20, minute=0) - timedelta(days=args.days_before)
    end_date = datetime.now().replace(hour=20, minute=0) + timedelta(days=args.days_after)
    
    if args.repository:
        repo_name = args.repository.split('/')[-1].split('.')[0]
    else:
        repo_name = 'generated_repo_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    
    repo = GitRepository(directory=repo_name, user_name=args.user_name, user_email=args.user_email)
    repo.initialize()

    commit_dates = generate_commit_dates(start_date, end_date, args.frequency, args.no_weekends, args.max_commits)
    for commit_date in commit_dates:
        repo.commit(message=f"Auto-generated commit on {commit_date.strftime('%Y-%m-%d')}", date=commit_date)

    if args.repository:
        repo.run_command(['git', 'remote', 'add', 'origin', args.repository])
        repo.run_command(['git', 'push', '-u', 'origin', 'main'])
    print("Repository generation completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit(f"Error: {e}")
