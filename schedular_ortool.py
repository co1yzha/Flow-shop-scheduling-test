# https://github.com/google/or-tools/tree/master/examples

import collections
from ortools.sat.python import cp_model # cp-sat solver
import pandas as pd
import glob
import plotly.io as pio
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

pio.renderers.default = 'browser'

# --- get job data
# template_path = './data/ExcelDataSpreadSheetBU.xlsx'
instance_dir = './data/test_instances/'
instance_list = glob.glob(f'{instance_dir}*.txt')
instance = instance_list[3]
file_name = instance.split('\\')[-1].replace('.txt','')
print(f'working on instance {file_name}')

# ----- read instance
with open(instance) as f:
    meta = f.readline().rstrip().split(' ')
n_jobs = int(meta[0])
n_ws = int(meta[1])
all_ws = range(n_ws)
n_operations = int(meta[2])

with open(instance) as f:
    data = f.readlines()[1:]

# ----- meta file
cols = ['release', 'due', 'n_ops', 'priority']
df_meta = pd.DataFrame(columns=cols)
for icol, idx in zip(cols, [0, 1, 3, 2]):
    df_meta[icol] = [int(float(data[i].rstrip().split(' ')[idx])) for i in range(0, n_jobs)]
idx = df_meta.sort_values(by='due').index
df_meta.loc[idx, 'priority'] = list(map(int, list(range(1, len(idx)+1))))
df_meta['job'] = df_meta.index.values
df_meta['priority1'] = [int((n-i+1)**3) for n,i in zip(df_meta['n_ops'], df_meta['priority'])]

# ----- jobs data reformat
jobs_data = [# task = (work_centre_id, processing_time).
     ]
for i_job in range(0, n_jobs):
    job_id = [int(i) for i in data[i_job].rstrip().split(' ')[4::2]]
    job_t = [int(i) for i in data[i_job].rstrip().split(' ')[5::2]]
    jobs_data.insert(i_job, [(i, j) for i, j in zip(job_id, job_t)])
horizon = sum(op[1] for job in jobs_data for op in job)

# ----- Model
model = cp_model.CpModel()

# ----- model:vars
op_type = collections.namedtuple('op_type', 'start end interval')
assigned_op_type = collections.namedtuple('assigned_op_type', 'start job index duration')

all_ops = {}
ws_to_intervals = collections.defaultdict(list)
for job_id, job in enumerate(jobs_data):
    for op_id, op in enumerate(job):
        ws = op[0]-1
        duration = op[1]
        suffix = f'_job{job_id}_op{op_id}'

        start_var = model.NewIntVar(0, horizon, f'start{suffix}')
        end_var = model.NewIntVar(0, horizon, f'end{suffix}')
        interval_var = model.NewIntervalVar(start_var, duration, end_var, f'interval{suffix}')
        all_ops[job_id, op_id] = op_type(start=start_var,
                                         end=end_var,
                                         interval=interval_var)
        ws_to_intervals[ws].append(interval_var)

# ----- model: constraints
# disjunctive constraints
for ws in all_ws:
    model.AddNoOverlap(ws_to_intervals[ws])
# precedences inside a job
for job_id, job in enumerate(jobs_data):
    for op_id in range(len(job)-1):
        model.Add(all_ops[job_id, op_id+1].start >= all_ops[job_id, op_id].end)



# ----- model: objective -> minimize weighted tardiness
# obj_var = model.NewIntVar(0, horizon, 'makespan')
# model.AddMaxEquality(obj_var, [all_ops[job_id, len(job)-1].end for
#                                job_id, job in enumerate(jobs_data)])

obj_var_rep = model.NewIntVar(0, horizon, 'lateness')
obj_var_rep = cp_model.LinearExpr.WeightedSum([(all_ops[job_id, len(job)-1].end - df_meta.loc[job_id, 'due'])
                               for job_id, job in enumerate(jobs_data)], df_meta.loc[:, 'priority1'])
model.Minimize(obj_var_rep)

#
# obj_var = [model.NewIntVar(1, horizon, f'tar_job{i}') for i in range(0, len(jobs_data))]
# obj_var1 = [model.NewIntVar(-horizon, horizon, f'tar_job{i}') for i in range(0, len(jobs_data))]
# #
# for job_id, job in enumerate(jobs_data):
#     ta = model.NewBoolVar(f'tardiness')
#     v = model.NewIntVar(-horizon, horizon, f'temp')
#     model.Add(v == all_ops[job_id, len(job) - 1].end - df_meta.loc[job_id, 'due'])
#     model.AddAbsEquality(obj_var[job_id], v)
#     model.AddDivisionEquality(obj_var1[job_id], v, obj_var[job_id])
#
# obj_var_rep = cp_model.LinearExpr.Sum([(all_ops[job_id, len(job)-1].end - df_meta.loc[job_id, 'due'])>0
#                                for job_id, job in enumerate(jobs_data)])
# model.Minimize(obj_var_rep)
#

# obj_var_rep = cp_model.LinearExpr.WeightedSum([(all_ops[job_id, len(job) - 1].end - df_meta.loc[job_id, 'due'])/obj_var[job_id]
#                                                for job_id, job in enumerate(jobs_data)], df_meta.loc[:, 'priority1'])
#
#
#     model.Add(all_ops[job_id, len(job) - 1].end - df_meta.loc[job_id, 'due'] > 0).OnlyEnforceIf(ta)
#     model.Add(all_ops[job_id, len(job) - 1].end - df_meta.loc[job_id, 'due'] <= 0).OnlyEnforceIf(ta.Not()) # late
#     model.Add(obj_var[job_id]==(all_ops[job_id, len(job) - 1].end - df_meta.loc[job_id, 'due']))

# model.Minimize(obj_var_rep)


# Solver
solver = cp_model.CpSolver()
# solver.parameters.log_search_progress = True
status = solver.Solve(model)

# Display
if status == cp_model.OPTIMAL or status==cp_model.FEASIBLE:
    temp = []
    for job_id, job in enumerate(jobs_data):

        for op_id, op in enumerate(job):
            ws = op[0]
            temp.append({
                'job': job_id,
                'operation': op_id,
                'work centre': ws,
                'start': solver.Value(all_ops[job_id, op_id].start),
                'duration': op[1]
                    })
    df_sol_op = pd.DataFrame(temp)
    df_sol_op = df_sol_op.merge(df_meta[['job', 'due', 'n_ops', 'priority1', 'priority']], on='job')
    df_sol_op['end'] = df_sol_op['start'] + df_sol_op['duration']

    print('\n ----- Solution: -----')
    # assigned op per work station/centre
    assigned_jobs = collections.defaultdict(list)
    for job_id, job in enumerate(jobs_data):
        for op_id, op in enumerate(job):
            ws = op[0]
            assigned_jobs[ws].append(
                assigned_op_type(
                    start = solver.Value(all_ops[job_id, op_id].start),
                    job=job_id,
                    index=op_id,
                    duration=op[1]
                )
            )

    # Create per work centre output lines.
    output = ''
    for ws in all_ws:
        assigned_jobs[ws].sort()
        sol_line_ops = 'Work Centre' + str(ws) + ':'
        sol_line = '      '

        for assigned_op in assigned_jobs[ws]:
            name = 'job_%i_op_%i' % (assigned_op.job, assigned_op.index)
            sol_line_ops += '%-15s' % name
            start = assigned_op.start
            duration = assigned_op.duration
            sol_tmp = '[%i, %i]' % (start, start+duration)
            sol_line += '%-15s' %sol_tmp

        sol_line += '\n'
        sol_line_ops += '\n'
        output += sol_line_ops
        output += sol_line

    print(f'Optimal Schedule Length: {solver.ObjectiveValue()}')
    print(output)

else:
    print('No solution fund')

# Statistics
print('\nStatistics')
print('  - conflicts: %i' % solver.NumConflicts())
print('  - branches : %i' % solver.NumBranches())
print('  - wall time: %f s' % solver.WallTime())

# df_sol_op.to_csv(f'./data/ortool/{file_name}.csv', index=False)

# -- Gantt chart
df1 = df_sol_op.rename(columns={'start':'Start', 'end':'Finish', 'job':'Task'})
df1['Task'] = df1['Task'].apply(lambda a:f"job_no{a+1}")
df1['Work Centre'] = df1['work centre'].apply(lambda a:f"Work Centre {a}")
df1 = df1.sort_values(by=['priority', 'work centre']).reset_index(drop=True)

df_due = df1[['Task', 'priority']].groupby(['Task']).mean()
df_due.reset_index(inplace=True)
df_due = df_due.merge(df_meta[['priority', 'due', 'job']], left_on='priority', right_on='priority')
df_due['priority'] = df_due['priority'].max() - df_due['priority']

N = len(df1['Work Centre'].unique())
cls = px.colors.qualitative.Set3
cls_dict = {f"Work Centre {i+1}": j for i, j in zip(range(0, N), cls[0:N]) }

fig1 = ff.create_gantt(df1, colors = cls_dict,
                       index_col='Work Centre',
                       show_colorbar=True,
                       group_tasks=True,
                       showgrid_x=True,
                       showgrid_y=True)
fig1.add_trace(go.Scatter(x=df_due['due'], y=df_due['priority'], mode='markers',
                          marker_line_width=2, marker_size=16, name='Due'))
fig1.update_layout(title_text=f'ORTool: {file_name}', xaxis_title='Minutes',
                   xaxis_type='linear',
                   xaxis = dict(range = [-50, 1500], tickvals=list(range(0, 2401, 200))),
                   autosize=True, font = dict(size=16))
fig1.show()