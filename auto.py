#!/usr/bin/python3
        
"""
Author : Robert Y. Stanford(GitHub @RYSF13)
Repo   : https://github.com/RYSF13/ad-astra
LICENSE: MIT
"""

import sys
import subprocess
import time

def format_number(num):
    if num >= 1000000:
        return f"{num / 1000000:.1f}m"
    elif num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)

def print_progress(current, total, is_pushing=False):
    spinners = ['|', '/', '-', '\\']
    spinner = spinners[current % 4]

    bar_length = 20
    progress = int((current / total) * bar_length)
    bar = '|' * progress + '.' * (bar_length - progress)

    percent = int((current / total) * 100)

    formatted_current = format_number(current)
    formatted_total = format_number(total)

    status = " PUSHING" if is_pushing else "        "

    sys.stdout.write(f"\r{spinner} [{bar}] {formatted_current}/{formatted_total} {percent:02d}%{status}")
    sys.stdout.flush()

def get_git_config(key):
    try:
        return subprocess.check_output(['git', 'config', '--get', key]).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        print(f"\n[FATAL] Missing git config: {key}")
        print(f"Run 'git config user.name \"Name\"' and 'git config user.email \"email\"'")
        sys.exit(1)

def get_current_branch():
    try:
        branch = subprocess.check_output(['git', 'branch', '--show-current']).decode('utf-8').strip()
        return branch if branch else "main"
    except subprocess.CalledProcessError:
        return "main"


def get_branch_tip(branch):
    try:
        return subprocess.check_output(['git', 'rev-parse', f'refs/heads/{branch}']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None

def main():
    print("AD ASTRA PER ASPERA")
    print("====================")
    print("")

    try:
        total_input = input("Total commits (10000): ")
        total_commits = int(total_input) if total_input.strip() else 10000
    except ValueError:
        total_commits = 10000

    try:
        batch_input = input("Push batch size (2500): ")
        push_batch = int(batch_input) if batch_input.strip() else 2500
    except ValueError:
        push_batch = 2500

    if push_batch > total_commits:
        push_batch = total_commits

    print(f"Target: {total_commits} commits, Push every: {push_batch} commits.")
    print("Igniting warp drive...\n")

    author_name = get_git_config('user.name')
    author_email = get_git_config('user.email')
    branch = get_current_branch()
    
    commit_msg = "Ad astra per aspera\n"
    msg_len = len(commit_msg.encode('utf-8'))

    current_commit = 0

    while current_commit < total_commits:
        
        
        tip = get_branch_tip(branch)
        
        batch_size = min(push_batch, total_commits - current_commit)

        p = subprocess.Popen(
            ['git', 'fast-import', '--quiet'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE
        )

        is_first_of_batch = True

        for _ in range(batch_size):
            current_commit += 1
            
            timestamp = int(time.time())
            timezone = "+0800"

            
            payload = f"commit refs/heads/{branch}\n"
            payload += f"committer {author_name} <{author_email}> {timestamp} {timezone}\n"
            payload += f"data {msg_len}\n{commit_msg}"
            
            
            if is_first_of_batch and tip:
                payload += f"from {tip}\n"
            
            payload += "\n" 
            
            is_first_of_batch = False
            
            try:
                p.stdin.write(payload.encode('utf-8'))
            except BrokenPipeError:
                break 

            print_progress(current_commit, total_commits)

        try:
            p.stdin.close()
        except BrokenPipeError:
            pass 

        p.wait()

        if p.returncode != 0:
            error_msg = p.stderr.read().decode('utf-8').strip()
            print(f"\n\n[FATAL] git fast-import engine failure.")
            print(f"Git Error: {error_msg}")
            sys.exit(1)

        print_progress(current_commit, total_commits, is_pushing=True)
        subprocess.run(
            ["git", "gc", "--aggressive"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        result = subprocess.run(
            ["git", "push", "origin", branch],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:
            print("\nError: Push failed. GitHub might be throttling you or you have network issues.")
            sys.exit(1)

        if current_commit != total_commits:
            print_progress(current_commit, total_commits)

    print("\n\nMission accomplished!")

if __name__ == "__main__":
    main()
