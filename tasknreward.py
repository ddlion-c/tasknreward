import click
import os
import io
import json
import pickle
import datetime
import random

DEFAULT_PARAMETERS = {
    'daily_task_list': [],
    'monthly_task_list': [],
    'annually_task_list': [],
    'weekly_reward_list': [],
    'monthly_reward_list': [],
    'annually_reward_list': []
}

DEFAULT_RECORD = {
    'date': None,
    'daily_score': 0,
    'monthly_score': 0,
    'annually_score': 0,
    'daily_reset_limit': 3,
    'd_pending_task_list': [],
    'd_completed_task_list': [],
    'm_pending_task_list': [],
    'm_completed_task_list': [],
    'a_pending_task_list': [],
    'a_completed_task_list': []
}


class Parameters:
    def __init__(self, override):
        self.update(DEFAULT_PARAMETERS)
        self.update(override)

    def update(self, override):
        for key, value in override.items():
            if key in DEFAULT_PARAMETERS:
                setattr(self, key, value)

    @property
    def n_wtask(self):
        return len(self.daily_task_list)

    @property
    def n_mtask(self):
        return len(self.monthly_task_list)

    @property
    def n_atask(self):
        return len(self.annually_task_list)

    @staticmethod
    def from_json(fp):
        return Parameters(json.load(fp))


class Record:
    def __init__(self, override):
        self.update(DEFAULT_RECORD)
        self.update(override)

    def update(self, override):
        for key, value in override.items():
            if key in DEFAULT_RECORD:
                setattr(self, key, value)

    def reset(self, level):
        if level == 'd':
            self.daily_score = 0
        elif level == 'm':
            self.monthly_score = 0
        elif level == 'a':
            self.annually_score = 0
        else:
            return

    def update_score(self, level, score):
        if level == 'd':
            self.daily_score = score
        elif level == 'm':
            self.monthly_score += score
        elif level == 'a':
            self.annually_score += score
        else:
            return

    @staticmethod
    def from_json(fp):
        return Record(json.load(fp))

    @staticmethod
    def to_json(obj):
        save_obj = {}
        for key in DEFAULT_RECORD:
            save_obj.update({key: getattr(obj, key)})

        return save_obj


@click.group()
def main():
    """Tasks&Rewards"""


@click.command(name='task')
@click.option('--level', '-l',
              type=click.STRING,
              default='all',
              help='Display task level, default is all and will display all three levels of tasks. Other options are w, m and a'
              )
@click.argument('parameters', type=click.File(), default='parameter.json')
def task(level, parameters):
    params = Parameters.from_json(parameters)
    nl = '\n'

    if level == 'all':
        click.echo(f"{nl}Daily Task List{nl}{'=' * 29}")
        print(params.daily_task_list)
        click.echo(f"{nl}Monthly Task List{nl}{'=' * 29}")
        print(params.monthly_task_list)
        click.echo(f"{nl}Annually Task List{nl}{'=' * 29}")
        print(params.annually_task_list)
    elif level == 'd':
        click.echo(f"{nl}Daily Task List{nl}{'=' * 29}")
        print(params.daily_task_list)
    elif level == 'm':
        click.echo(f"{nl}Monthly Task List{nl}{'=' * 29}")
        print(params.monthly_task_list)
    elif level == 'a':
        click.echo(f"{nl}Annually Task List{nl}{'=' * 29}")
        print(params.annually_task_list)
    else:
        print("Task level not recognized, please input any valid options between: all, w, m a")


@click.command(name='reward')
@click.option('--level', '-l',
              type=click.STRING,
              default='all',
              help='Display reward level, default is all and will display all three levels of tasks. Other options are w, m and a'
              )
@click.argument('parameters', type=click.File(), default='parameter.json')
def reward(level, parameters):
    params = Parameters.from_json(parameters)
    nl = '\n'
    if level == 'all':
        click.echo(f"{nl}Weekly Reward List{nl}{'=' * 29}")
        print(params.weekly_reward_list)
        click.echo(f"{nl}Monthly Reward List{nl}{'=' * 29}")
        print(params.monthly_reward_list)
        click.echo(f"{nl}Annually Reward List{nl}{'=' * 29}")
        print(params.annually_reward_list)
    elif level == 'w':
        click.echo(f"{nl}Weekly Reward List{nl}{'=' * 29}")
        print(params.weekly_reward_list)
    elif level == 'm':
        click.echo(f"{nl}Monthly Reward List{nl}{'=' * 29}")
        print(params.monthly_reward_list)
    elif level == 'a':
        click.echo(f"{nl}Annually Reward List{nl}{'=' * 29}")
        print(params.annually_reward_list)
    else:
        print("Reward level not recognized, please input any valid options between: all, w, m a")


@click.command(name='score')
@click.option('--level', '-l',
              type=click.STRING,
              default='all',
              help='Display score level, default is all and will display all three levels of tasks. Other options are w, m and a'
              )
def score(level):
    file_path = "record.json"
    nl = '\n'

    if not os.path.exists(file_path):
        with open(file_path, "w") as fp:
            json.dump(DEFAULT_RECORD, fp, indent=4)
            click.echo(f"{nl}Score record created")
    else:
        click.echo(f"{nl}Score record loaded")

    with open(file_path, "r") as fp:
        score = Record.from_json(fp)

    if level == 'all':
        click.echo(f"{nl}Daily Score: {score.daily_score}")
        click.echo(f"{nl}Monthly Score: {score.monthly_score}")
        click.echo(f"{nl}Annually Score: {score.annually_score}")
    elif level == 'w':
        click.echo(f"{nl}Daily Score: {score.daily_score}")
    elif level == 'm':
        click.echo(f"{nl}Monthly Score: {score.monthly_score}")
    elif level == 'a':
        click.echo(f"{nl}Annually Score: {score.annually_score}")
    else:
        print("Score level not recognized, please input any valid options between: all, w, m a")


@click.command(name='generate', help='Generate daily tasks')
def generate():
    p_path = 'parameter.json'
    r_path = 'record.json'
    t_path = 'task.txt'
    nl = '\n'

    dot = datetime.datetime.today().date()
    dow = datetime.datetime.today().weekday() + 1

    if not os.path.exists(p_path) or not os.path.exists(r_path):
        click.echo(f"Both parameter and record files should exist")
    else:
        with open(p_path, "r") as fp:
            parameter = Parameters.from_json(fp)

        with open(r_path, "r") as fp:
            record = Record.from_json(fp)

        daily_task = random.sample(parameter.daily_task_list, 2)
        click.echo(f"Today is {dot}, the day of week is {dow}, daily tasks are: {nl} {daily_task}")
        record.update({'date': str(dot)})
        record.update({'d_pending_task_list': daily_task})

        with open(r_path, "w") as fp:
            json.dump(Record.to_json(record), fp, indent=4)

        with open(t_path, 'w') as fp:
            for item in daily_task:
                # write each item on a new line
                fp.write("%s\n" % item)
            click.echo(f"Tasks have written to: {t_path}")


@click.command(name='complete', help='Complete task by reading the txt file')
def complete():
    t_path = 'task.txt'
    r_path = 'record.json'
    if not os.path.exists(t_path):
        click.echo(f"Task file does not exist")
    elif not os.path.exists(r_path):
        click.echo(f"Record file does not exist")
    else:
        with open(t_path) as file:
            temp_tasks = [line.rstrip() for line in file]
        with open(r_path, "r") as fp:
            record = Record.from_json(fp)
        # get pending task list, get completed task list, get task list
        p_task = record.d_pending_task_list
        c_task = record.d_completed_task_list
        # daily task = pending task + completed task
        d_task = p_task.copy()
        d_task.extend(c_task)
        # if task in task list can be found in pending task, retain the task in pending task list
        p_task = [t for t in temp_tasks if t in p_task]  # new pending task list
        c_task = [t for t in d_task if t not in p_task]  # new completed task list

        record.update({"d_pending_task_list": p_task, "d_completed_task_list": c_task})
        record.update_score('d', len(c_task) * 10)  # directly update score based on number of completed tasks

        with open(r_path, "w") as fp:
            json.dump(Record.to_json(record), fp, indent=4)

        # TODO: handle if the task can not be found in either pending task or completed task, append to additional task


@click.command(name="refresh", help="Refresh the pending tasks")
def refresh():
    r_path = "record.json"
    p_path = "parameter.json"
    t_path = "task.txt"
    if not os.path.exists(r_path):
        click.echo(f"Record file does not exist")
    elif not os.path.exists(p_path):
        click.echo(f"Parameter file does not exist")

    # Check if refresh limit is already zero, if so, quit with warning
    with open(r_path, "r") as fp:
        record = Record.from_json(fp)
    if record.daily_reset_limit <= 0:
        click.echo(f"Exceed refresh limit")
        return
    with open(p_path, "r") as fp:
        param = Parameters.from_json(fp)

    # Read full task list from parameter file
    full_task = param.daily_task_list
    # Read pending task list from record file
    old_pending = record.d_pending_task_list
    # Remove pending tasks from full task list and generate random tasks based on length of pending task list
    new_pending = random.sample([t for t in full_task if t not in old_pending], len(old_pending))
    # Deduct one refresh limit
    record.update({'daily_reset_limit': (record.daily_reset_limit - 1), 'd_pending_task_list': new_pending})
    with open(r_path, "w") as fp:
        json.dump(Record.to_json(record), fp, indent=4)
    # Generate new task list
    with open(t_path, 'w') as fp:
        for item in new_pending:
            # write each item on a new line
            fp.write("%s\n" % item)
        click.echo(f"Refreshed tasks have written to: {t_path}")


main.add_command(task)
main.add_command(reward)
main.add_command(score)
main.add_command(generate)
main.add_command(complete)
main.add_command(refresh)

if __name__ == '__main__':
    main()
