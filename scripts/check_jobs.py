import yaml
import subprocess
import re

def get_changed_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True, text=True, check=False
    )
    return result.stdout.strip().splitlines()

def check_jobs():
    errors = []
    changed = get_changed_files()

    for file in changed:
        if not file.endswith((".yml", ".yaml")):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                job = yaml.safe_load(f)
        except Exception:
            errors.append(f"❌ Could not parse job YAML: {file}")
            continue

        # Must have "dag" block
        dag = job.get("dag")
        if not dag:
            errors.append(f"❌ Job {file} missing top-level 'dag' block")
            continue

        # Rule 1: dag_id must follow jb_<3 letters>_<desc>
        dag_id = dag.get("dag_id")
        if not dag_id:
            errors.append(f"❌ Job {file} missing 'dag_id'")
        elif not re.match(r"^jb_[a-z]{3}_.+$", dag_id):
            errors.append(f"❌ Job {file} has invalid dag_id '{dag_id}' (expected jb_<3-letter>_<desc>)")

        # Rule 2: schedule_interval must be valid cron
        schedule = dag.get("schedule_interval")
        if not schedule:
            errors.append(f"❌ Job {file} missing 'schedule_interval'")
        elif not re.match(r"^(\S+\s+){4}\S+$", str(schedule).strip('"').strip("'")):
            errors.append(f"❌ Job {file} has invalid cron expression: {schedule}")

        # Rule 3: default_args.owner must exist
        default_args = dag.get("default_args", {})
        if "owner" not in default_args:
            errors.append(f"❌ Job {file} missing default_args.owner")

        # Rule 4: Must define tasks
        tasks = job.get("tasks")
        if not tasks or not isinstance(tasks, list):
            errors.append(f"❌ Job {file} missing 'tasks' list")
        else:
            for t in tasks:
                task_id = t.get("task_id")
                if not task_id:
                    errors.append(f"❌ Job {file} has task without 'task_id'")
                elif not task_id.startswith("tsk_"):
                    errors.append(f"❌ Job {file} task_id '{task_id}' must start with 'tsk_'")

                operator = t.get("operator")
                if not operator:
                    errors.append(f"❌ Job {file} task {task_id} missing 'operator'")

    return errors
