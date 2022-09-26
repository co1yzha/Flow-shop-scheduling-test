"""
https://developers.google.com/optimization/introduction/python
Example job shop problem:
(m, p) ->  m: number of the machine; p: processing time of the task
job 0 = [(0, 3), (1, 2), (2, 2)]
job 1 = [(0, 2), (2, 1), (1, 4)]
job 2 = [(1, 4), (2, 3)]
job 3 = [(0, 3), (1, 2), (2, 2)]

task(1, j) => jth task in the sequence for job i
ti,j => start time for task(i,j)

"""

# 1. Import packages
import collections
from ortools.sat.python import cp_model

# 2. Define data
jobs_data = [
    # task = (machine_id, processing_time).
    [(0, 3), (1, 2), (2, 2)], # Job0
    [(0, 2), (2, 1), (1, 4)], # Job1
    [(1, 4), (2, 3)], # Job2
    [(0, 3), (1, 2), (2, 2)] # Job3
]

machines_count = 1 + max(task[0] for job in jobs_data for task in job)
all_machines = range(machines_count)
# Computes horizon dynamically as the sum of all durations
horizon = sum(task[1] for job in jobs_data for task in job)


# 3. Declare the model
model = cp_model.CpModel()

# 4. Define variables
# Named tuple to store information about created variables.
task_type = collections.namedtuple('task_type', 'start end interval')
# Named tuple to manipulate solution information.
assigned_task_type = collections.namedtuple('assigned_task_type', 'start job index duration')
# Creates job intervals and add to the corresponding machine lists.
all_tasks={}
machine_to_intervals = collections.defaultdict(list)
for job_id, job in enumerate(jobs_data):
    for task_id, task in enumerate(job):
        machine = task[0]
        duration = task[1]
        suffix = f'_{job_id}_{task_id}'

        start_var = model.NewIntVar(0, horizon, 'start' + suffix)
        end_var = model.NewIntVar(0, horizon, 'end' + suffix)
        interval_var = model.NewIntervalVar(start_var, duration, end_var, 'interval'+suffix)
        all_tasks[job_id, task_id] = task_type(start=start_var, end=end_var, interval=interval_var)
        machine_to_intervals[machine].append(interval_var)

# 5. Define the constraints
# 5.1 Disjunctive constraints
for machine in all_machines:
    model.AddNoOverlap(machine_to_intervals[machine])

# 5.2 Precedences inside a job.
for job_id, job in enumerate(jobs_data):
    for task_id in range(len(job)-1):
        model.Add(all_tasks[job_id, task_id+1].start >= all_tasks[job_id, task_id].end)


# 6. Define the objective
obj_var = model.NewIntVar(0, horizon, 'makespan')
model.AddMaxEquality(obj_var, [all_tasks[job_id, len(job)-1].end for job_id, job in enumerate(jobs_data)])
model.Minimize(obj_var)


# 7. Solver
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 8. Results Vis
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('Solution:')
    # Create one list of assigned tasks per machine.
    assigned_jobs = collections.defaultdict(list)
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            assigned_jobs[machine].append(
                assigned_task_type(start=solver.Value(
                    all_tasks[job_id, task_id].start),
                                   job=job_id,
                                   index=task_id,
                                   duration=task[1]))

    # Create per machine output lines.
    output = ''
    for machine in all_machines:
        # Sort by starting time.
        assigned_jobs[machine].sort()
        sol_line_tasks = 'Machine ' + str(machine) + ': '
        sol_line = '           '

        for assigned_task in assigned_jobs[machine]:
            name = 'job_%i_task_%i' % (assigned_task.job,
                                       assigned_task.index)
            # Add spaces to output to align columns.
            sol_line_tasks += '%-15s' % name

            start = assigned_task.start
            duration = assigned_task.duration
            sol_tmp = '[%i,%i]' % (start, start + duration)
            # Add spaces to output to align columns.
            sol_line += '%-15s' % sol_tmp

        sol_line += '\n'
        sol_line_tasks += '\n'
        output += sol_line_tasks
        output += sol_line

    # Finally print the solution found.
    print(f'Optimal Schedule Length: {solver.ObjectiveValue()}')
    print(output)
else:
    print('No solution found.')

# Statistics
print('\nStatistics')
print('  - conflicts: %i' % solver.NumConflicts())
print('  - branches : %i' % solver.NumBranches())
print('  - wall time: %f s' % solver.WallTime())