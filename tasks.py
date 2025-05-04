from invoke import task, Collection, Program
from pathlib import Path

@task
def run_main(ctx):
    """Run the main file from the src folder."""
    script_dir = Path(__file__).parent
    ctx.run(f"python {script_dir}\src\main.py .")



ns = Collection(run_main) 

if __name__ == "__main__":
    program = Program(namespace=ns)
    program.run()