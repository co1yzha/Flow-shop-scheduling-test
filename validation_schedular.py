import pandas as pd
import datetime
import glob
import businesstimedelta
from math import floor
import plotly.io as pio
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import matplotlib.pyplot as plt

pio.renderers.default = 'browser'


delta_list = []

for i_instance in [3]:#range(0, 22):
    # ----- Business time delta
    workday = businesstimedelta.WorkDayRule(
        start_time=datetime.time(9),
        end_time=datetime.time(17),
        working_days=[0, 1, 2, 3, 4])

    businesshrs = businesstimedelta.Rules([workday])


    # --- get df meta
    instance_dir = './data/test_instances/'
    instance_list = glob.glob(f'{instance_dir}*.txt')
    instance = instance_list[i_instance]
    file_name = instance.split('\\')[-1].replace('.txt','')

    ff_output = f'data/FF_schedular/{file_name}.xlsx'
    ps_output = f'data/priority_schedular/{file_name}.csv'

    print(f'working on instance {i_instance}:{file_name}')

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
    df_meta['priority1'] = [int((n-i+1)**2) for n,i in zip(df_meta['n_ops'], df_meta['priority'])]
    df_meta['job_len'] = [sum(list(map(int, data[i].rstrip().split(' ')[5::2]))) for i in range(0, len(data))]


    # -- read ff solution
    df_jobs = pd.read_excel(ff_output, sheet_name='jobs')
    df_ops = pd.read_excel(ff_output, sheet_name='ops')

    keep_cols = ['Job', 'Sequence', 'Work Centre', 'Priority', 'Scheduled Start Date', 'Scheduled End Date']
    df_ops = df_ops[keep_cols].copy()
    start0 = df_ops['Scheduled Start Date'].min()
    for i in df_ops.index:
        start = df_ops.loc[i, 'Scheduled Start Date']
        end = df_ops.loc[i, 'Scheduled End Date']
        bdiff0 = businesshrs.difference(start0, start)
        df_ops.loc[i, 'start0'] = bdiff0.hours*60 + bdiff0.seconds/60
        bdiff1 = businesshrs.difference(start0, end)
        df_ops.loc[i, 'end0'] = bdiff1.hours * 60 + bdiff1.seconds/60

    df_ops = df_ops.sort_values(by=['Priority', 'Job', 'Sequence']).reset_index(drop=True)
    df_ws = df_ops.sort_values(by=['start0', 'Work Centre', 'Priority', 'Sequence'])

    df_sol_jobs = pd.DataFrame(df_ops.groupby('Job')['Priority'].mean())
    df_sol_jobs['Job_no'] = df_sol_jobs.index.values
    df_sol_jobs['job'] = df_sol_jobs['Job_no'].apply(lambda a: int(a.split('_no')[1])-1)
    df_sol_jobs['start'] = df_ops.groupby('Job').min()['start0']
    # df_sol_jobs['start']= [floor(id) for id in df_sol_jobs['start']]
    df_sol_jobs['end'] = df_ops.groupby('Job').max()['end0']
    # df_sol_jobs['end'] = [floor(id) for id in df_sol_jobs['end']]
    df_sol_jobs.reset_index(drop=True, inplace=True)
    df_sol_jobs = df_sol_jobs.merge(df_meta[['job', 'due', 'job_len']], on='job')
    df_sol_jobs = df_sol_jobs.sort_values(by='Priority').reset_index(drop=True)

    # ---- read priority_schedular output
    ps_output = f'data/priority_schedular/{file_name}.csv'
    df_ps = pd.read_csv(ps_output)
    df_ps = df_ps.sort_values(by=['priority', 'job', 'sequence']).reset_index(drop=True)
    df_sol_ps = pd.DataFrame(df_ps.groupby('job')['priority', 'job'].mean())
    df_sol_ps['job'] = df_sol_ps['job'].astype(int)
    df_sol_ps['start'] = df_ps.groupby('job').min()['start']
    df_sol_ps['end'] = df_ps.groupby('job').max()['end']
    df_sol_ps['duration'] = df_sol_ps['end'] - df_sol_ps['start']
    # df_sol_ps['due'] = df_ps.groupby('job').mean()['due']
    df_sol_ps['job_len'] = df_ps.groupby('job').sum()['duration']

    df_sol_ps.sort_values(by='priority', inplace=True)
    df_sol_ps.reset_index(drop=True, inplace=True)


    delta_start = abs(df_sol_jobs['start'] - df_sol_ps['start'])
    delta_end =  abs(df_sol_jobs['end'] - df_sol_ps['end'])
    mae =  sum([i + j for i, j in zip(delta_start, delta_end)])/len(delta_start)/2
    # # df_sol_or = df_sol_or.merge(df_meta[['job', 'priority']], on='job')
    print(f"MAE is {mae}\n\n\n")

    delta_list= delta_list + list(df_sol_jobs['start'] - df_sol_ps['start']) \
                + list(df_sol_jobs['end'] - df_sol_ps['end'])


# ----- vis
fig = go.Figure()
fig.add_trace(go.Histogram(
    x = delta_list,
    name = 'delta',
    xbins=dict(start=-6, end=6, size=0.1),
    opacity = 0.75
))
fig.update_layout(
    title_text = 'Job Schedule Difference',
    yaxis_title_text = 'Count',
    xaxis_title_text = 'Minutes',
    font = dict(size=16)
)
fig.show()


# -- Gantt chart
df1 = df_ops.rename(columns={'start0':'Start', 'end0':'Finish', 'Job':'Task'})
df1['Work Centre'] = df1['Work Centre'].apply(lambda a:f"Work Centre {a.split('ws')[1]}")

df_due = df1[['Task', 'Priority']].groupby(['Task']).mean()
df_due.reset_index(inplace=True)
df_due = df_due.merge(df_meta[['priority', 'due', 'job']], left_on='Priority', right_on='priority')
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

fig1.update_layout(title_text=f'FFScheduler: {file_name}', xaxis_title='Minutes',
                   xaxis_type='linear',
                   xaxis = dict(range = [-50, 1450], tickvals=list(range(0, 1401, 200))),
                   autosize=True, font = dict(size=16))

fig1.show()



# -- Gantt chart verification
df2 = df_ps.rename(columns={'start':'Start', 'end':'Finish', 'job':'Task'})
df2['Work Centre'] = df2['ws'].apply(lambda a:f"Work Centre {int(a)}")
df2['Task'] = df2['Task'].apply(lambda a:f"job_no{int(a+1)}")

df_due2 = df2[['Task', 'priority']].groupby(['Task']).mean()
df_due2.reset_index(inplace=True)
df_due2 = df_due2.merge(df_meta[['priority', 'due', 'job']], left_on='priority', right_on='priority')
df_due2['priority'] = df_due2['priority'].max() - df_due2['priority']

N = len(df2['Work Centre'].unique())
cls = px.colors.qualitative.Set3
cls_dict = {f"Work Centre {i+1}": j for i, j in zip(range(0, N), cls[0:N]) }


fig2 = ff.create_gantt(df2, colors = cls_dict,
                       index_col='Work Centre',
                       show_colorbar=True,
                       group_tasks=True,
                       showgrid_x=True,
                       showgrid_y=True)
fig2.add_trace(go.Scatter(x=df_due2['due'], y=df_due2['priority'], mode='markers',
                          marker_line_width=2, marker_size=16, name='Due'))

fig2.update_layout(title_text=f'Verification of FFScheduler: {file_name}', xaxis_title='Minutes',
                   xaxis_type='linear',
                   xaxis = dict(range = [-10, 1450], tickvals=list(range(0, 2401, 300))),
                   autosize=True, font = dict(size=16))

fig2.show()

# df1 = df_ops.rename(columns={'start0':'Start', 'end0':'Finish', 'Work Centre':'Task'})
# df1['Priority'] = df1['Priority']*10
# fig2 = ff.create_gantt(df1, index_col='Priority', show_colorbar=True, group_tasks=True)
# fig2.update_layout(xaxis_type='linear', autosize=True)
# fig2.show()


#
# # df_sol_ws = df_ops.groupby(['Work Centre', 'Job', 'Sequence'])['start0', 'end0', 'Priority'].mean()
# # df_sol_ws = df_sol_ws.sort_values(by='start0')
# # df_sol_jobs.drop(columns=['job'], inplace=True)
# #
# #
# #
# # t0 = df_sol_jobs['Start'].min()
# # for idx in df_sol_jobs.index:
# #     end = df_sol_jobs.loc[idx, 'End']
# #     start = df_sol_jobs.loc[idx, 'Start']
# #     bdiff = businesshrs.difference(start, end)
# #     df_sol_jobs.loc[idx, 'duration'] = bdiff.hours*60 + bdiff.seconds/60
# #
# #     bdiff0 =  businesshrs.difference(t0, start)
# #     df_sol_jobs.loc[idx, 'start0'] = bdiff0.hours * 60 + bdiff0.seconds / 60
# #     bdiff1 = businesshrs.difference(t0, end)
# #     df_sol_jobs.loc[idx, 'end0'] = bdiff1.hours * 60 + bdiff1.seconds / 60
# #
# # df_sol_jobs['a'] = df_sol_jobs['duration'] - df_sol_jobs['job_len']
# #
# # # df_sol_jobs['Duration']
# # # df_sol_job['Idea]
# # # --------------------------------------------------------------------------

