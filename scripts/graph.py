"""
graph.py - prints the chain  agent -> identity -> tool -> data -> action.

One line per event. Bad ones are shown in red with the reason.
"""
import os

os.system("")  # makes colors work in the Windows terminal

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


def print_graph(results):
    current_agent = None
    for r in results:
        if r["agent"] != current_agent:
            current_agent = r["agent"]
            print(f"\n{current_agent}  (task: {r['task']})")

        chain = f"{r['agent']} -> {r['identity']} -> {r['tool']} -> {r['data']} -> {r['action']}"
        if r["problems"]:
            print(f"  {RED}[!] {chain}   <- {', '.join(r['problems'])}{RESET}")
        else:
            print(f"  {GREEN}[ok]{RESET} {chain}")
