import asyncio
from django.core.management.base import BaseCommand
from config import settings
from core.orchestrator import orchestrator


async def run_interactive_cli():
    """Terminal Command Interface for GHOST."""
    print("\n[GHOST TACTICAL CONSOLE ENGAGED]")
    print("Type your directive or 'exit' to terminate session.\n")
    while True:
        try:
            command = input(f"{settings.operator_name} >> ").strip()
            if not command:
                continue
            if command.lower() in ["exit", "quit", "abort"]:
                print("Session terminated. GHOST standing by in perimeter defense.")
                break

            result = await orchestrator.process_command(command)
            print(f"\n[GHOST] {result.get('response')}\n")
            if "plan" in result:
                checklist = result["plan"].get("checklist", [])
                print("--- MISSION OBJECTIVES ---")
                for task in checklist:
                    print(f"  [x] Task {task.get('task_id')}: {task.get('action')} (Clearance Level {task.get('level')})")
                print("--------------------------\n")

        except (KeyboardInterrupt, EOFError):
            break


class Command(BaseCommand):
    help = "Run the GHOST Tactical Terminal Console (interactive CLI)"

    def handle(self, *args, **options):
        asyncio.run(run_interactive_cli())

