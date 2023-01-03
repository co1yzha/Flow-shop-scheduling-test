import pandas as pd
import datetime
import glob
import numpy as np


# --- get df meta
i_instance = 3
instance_dir = './data/test_instances/'
instance_list = glob.glob(f'{instance_dir}*.txt')
instance = instance_list[i_instance]
file_name = instance.split('\\')[-1].replace('.txt','')
ff_output = f'data/FF_schedular/{file_name}.xlsx'

print(f'working on instance {i_instance}: {file_name}')

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
# df_meta['priority1'] = [int((n-i+1)**2) for n,i in zip(df_meta['n_ops'], df_meta['priority'])]
df_meta['job_len'] = [sum(list(map(int, data[i].rstrip().split(' ')[5::2]))) for i in range(0, len(data))]


# ----- ops
df_ops = pd.DataFrame(index=range(0, n_operations))
# df_ops['ClientId*'] = list(range(1, n_operations+1))
idx_op = 0
for i in range(0, len(data)):

    op_wc_idx = list(map(int, data[i].rstrip().split(' ')[4::2]))
    op_t = list(map(int, data[i].rstrip().split(' ')[5::2]))
    op_n = len(op_wc_idx)
    idx_temp = range(idx_op, op_n+idx_op)
    df_ops.loc[idx_temp, 'job'] = i
    df_ops.loc[idx_temp, 'ws'] = op_wc_idx
    df_ops.loc[idx_temp, 'sequence'] = [i*10 for i in list(range(1, op_n+1))]
    df_ops.loc[idx_temp, 'priority'] = df_meta.loc[i, 'priority']
    df_ops.loc[idx_temp, 'duration'] = [int(id) for id in op_t]
    idx_op = idx_op + op_n

horizon = int(df_ops['duration'].sum())
mat_ws = np.zeros((n_ws, horizon))


for i_priority in np.sort(df_ops['priority'].unique()):
    if i_priority == 8:
        print(i)

    df_temp = df_ops[df_ops['priority'] == i_priority]
    t0 = 0
    for idx in df_temp.index:
        op = df_temp.loc[idx, :]
        job = op['job']
        ws = int(op['ws']-1)
        t0 = int(t0)#start
        t1 = t0 + int(op['duration'])
        acc = mat_ws[ws, t0:t1].sum()
        # print(acc)
        if acc < 1:
            mat_ws[ws, t0:t1] = 1
            df_ops.loc[idx, 'start'] = t0
            df_ops.loc[idx, 'end'] = t1
            t0 = t1
        else:
            while acc:
                t0 = t0+1
                t1 = t0 + int(op['duration'])
                acc = mat_ws[ws, t0:t1].sum()
            mat_ws[ws, t0:t1] = 1
            df_ops.loc[idx, 'start'] = t0
            df_ops.loc[idx, 'end'] = t1
            t0 = t1

export_output = f'data/priority_schedular/{file_name}.csv'
df_ops.to_csv(export_output, index=False)
