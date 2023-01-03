'''
convert morton pentico instance to scheduler csv input
https://web.imt-atlantique.fr/x-auto/clahlou/mdl/Benchmarks.html

'''

import pandas as pd
import glob
import datetime
import random
import businesstimedelta

def get_sheet(template_f, sheet_name):
    df = template_f.parse(sheet_name)
    a_cols = [i for i in df.columns if 'Unnamed' not in i]
    df = df.loc[:, a_cols]
    df.drop(df.index, inplace=True)
    # df = pd.DataFrame(columns=a_cols)
    return df

for i_instance in [21]:

    workday = businesstimedelta.WorkDayRule(
        start_time=datetime.time(8),
        end_time=datetime.time(17),
        working_days=[0, 1, 2, 3, 4])

    businesshrs = businesstimedelta.Rules([workday])

    # def get_instance_list(dir='./data/singer pinedo/'):
    #     return glob.glob(f'{dir}*.txt')
    # df0 = pd.read_excel('data/ExcelDataSpreadSheetBU.xlsx', 'Jobs')
    template_path = './data/ExcelDataSpreadSheetBU.xlsx'
    instance_dir = './data/test_instances/'
    instance_list = glob.glob(f'{instance_dir}*.txt')
    instance = instance_list[i_instance]
    file_name = instance.split('\\')[-1].replace('.txt','.xlsx')
    print(f'working on instance {i_instance}: {file_name}')

    template_f = pd.ExcelFile(template_path)
    # sheet_names = template_f.sheet_names
    sheet_names = ['Work Centres', 'Jobs', 'Operations', 'Calendars', 'Calendar Records']
    df_wc = get_sheet(template_f, 'Work Centres')
    df_jobs = get_sheet(template_f, 'Jobs')
    df_operations = get_sheet(template_f, 'Operations')
    df_calendars = get_sheet(template_f, 'Calendars')
    df_records = get_sheet(template_f, 'Calendar Records')

    # ----- read instance
    with open(instance) as f:
        meta = f.readline().rstrip().split(' ')
    n_jobs = int(meta[0])
    n_ws = int(meta[1])
    n_operations = int(meta[2])

    with open(instance) as f:
        data = f.readlines()[1:]

    cols = ['release', 'due', 'n_ops', 'priority']
    df_meta = pd.DataFrame(columns=cols)
    for icol, idx in zip(cols, [0, 1, 3, 2]):
        df_meta[icol] = [float(data[i].rstrip().split(' ')[idx]) for i in range(0, n_jobs)]
    idx = df_meta.sort_values(by='due').index
    df_meta.loc[idx, 'priority'] = list(map(int, list(range(1, len(idx)+1))))
    # df_meta['requiredD1'] = [pd.Timestamp(datetime.datetime.now()) + pd.offsets.BusinessHour(int(h)) + pd.offsets.BusinessDay(1)
    #                         for h in df_meta['due']/60]
    df_meta['requiredD'] = [datetime.datetime.now() +
                            businesstimedelta.BusinessTimeDelta(businesshrs, seconds=h) for h in df_meta['due']*60]
    df_meta['requiredD'] = df_meta['requiredD'].dt.tz_localize(None)


    # ----- Work Centres Sheet
    df_wc['ClientId*'] = list(range(1, n_ws+1))
    df_wc['WorkCentreNo*'] = 'ws_no' + df_wc['ClientId*'].astype(str)
    df_wc['WorkCentreName*'] = 'ws' + df_wc['ClientId*'].astype(str)
    df_wc['WorkCentreDescription'] = 'ws_descrip' + df_wc['ClientId*'].astype(str)
    df_wc['Efficiency'] = 100
    df_wc['Infinite Capaciity'] = False
    df_wc['CalendarId'] = 1

    # ----- Jobs
    df_jobs['ClientId*'] = list(range(1, n_jobs+1))
    df_jobs['JobNo*'] = 'job_no' + df_jobs['ClientId*'].astype(str)
    df_jobs['PartNo*'] = 'part_no' + df_jobs['ClientId*'].astype(str)
    df_jobs['PartDescription'] = 'job_descrip' + df_jobs['ClientId*'].astype(str)
    df_jobs['SalesNo'] = 'sales' + df_jobs['ClientId*'].astype(str)
    df_jobs['Qty'] = random.sample(range(1, n_jobs*10), n_jobs)
    df_jobs['Customer'] ='c' + df_jobs['ClientId*'].astype(str)
    df_jobs['SaleValue'] = [i*1000 for i in random.sample(range(1, n_jobs*10), n_jobs)]
    df_jobs['Priority'] = df_meta['priority']
    df_jobs['DateRequired'] = df_meta['requiredD']#.apply(lambda a: a.strftime('%d/%m/%Y %H:%M'))

    # ----- Oprations
    df_operations['ClientId*'] = list(range(1, n_operations+1))

    idx_op = 0
    set_t = 0.1
    for i in range(0, len(data)):
        op_wc_idx = list(map(int, data[i].rstrip().split(' ')[4::2]))
        op_t = list(map(int, data[i].rstrip().split(' ')[5::2]))

        if min(op_t) < 6:
            print(op_t)
            print(min(op_t))
            set_t = 0

        op_n = len(op_wc_idx)
        idx_temp = range(idx_op, op_n+idx_op)
        df_operations.loc[idx_temp, ' JobId*'] = int(i + 1)
        df_operations.loc[idx_temp, 'OpNo*'] = ['op_no' + str(n) for n in list(range(1, op_n+1))]
        df_operations.loc[idx_temp, 'WorkCentreId'] = op_wc_idx
        df_operations.loc[idx_temp, 'Sequence'] = [i*10 for i in list(range(1, op_n+1))]
        df_operations.loc[idx_temp, ['PlannedSetTime', 'OutstandingSetTime']] = set_t
        df_operations.loc[idx_temp, 'PlannedRunTime'] = [round(id/60 - set_t, 2) for id in op_t]
        df_operations.loc[idx_temp, 'OutstandingRunTime'] =  [round(id/60 - set_t, 2) for id in op_t]
        df_operations.loc[idx_temp, 'Priority'] = df_meta.loc[i, 'priority']
        idx_op = idx_op + op_n

    df_operations['FirstStartDate'] = datetime.datetime.now()#.strftime('%d/%m/%Y %H:%M')
    df_operations['Locked'] = False
    df_operations['Scheduled'] = False
    df_operations['IsLive'] = False


    # Calendar
    df_calendars.loc[1, : ] = [1, 'TestCalendarName', 'TRUE']
    df_records.loc[1, :] = [1, 'Monday', '09:00:00', '17:00:00', 100, 1]


    excel_file = f"./data/converted_instances/{file_name}"
    with pd.ExcelWriter(excel_file) as writer:
        df_wc.to_excel(writer, sheet_name='Work Centres', index=False)
        df_jobs.to_excel(writer, sheet_name='Jobs', index=False)
        df_operations.to_excel(writer, sheet_name='Operations', index=False)
        df_calendars.to_excel(writer, sheet_name='Calendars', index=False)
        df_records.to_excel(writer, sheet_name='Calendar Records', index=False)
