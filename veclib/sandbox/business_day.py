import pandas as pd
import datetime
from pandas.tseries.offsets import CDay
from pandas.tseries.holiday import (
    AbstractHolidayCalendar, DateOffset, EasterMonday,
    GoodFriday, Holiday, MO,
    next_monday, next_monday_or_tuesday)

# This function will calculate the number of working minutes by first
# generating a time series of business days. Then it will calculate the
# precise working minutes for the start and end date, and use the total
# working hours for each day in-between.

def count_mins(starttime,endtime, bus_day_series, bus_start_time,bus_end_time):
    mins_in_working_day=(bus_end_time-bus_start_time)*60

    # now we are going to take the series of business days (pre-calculated)
    # and sub select the period provided as argument of the function
    # we could do the calculation of that "calendar" in the function itself
    # but to improve performance, we calculate it separately and then we c
    # call the function with that series as argument, provided the dates
    # fall within the calculated range, of course
    days = bus_day_series[starttime.date():endtime.date()]

    daycount = len(days)
    if len(days)==0:
        return 0
    else:
        first_day_start = days[0].replace(hour=bus_start_time, minute=0)
        first_day_end = days[0].replace(hour=bus_end_time, minute=0)
        first_period_start = max(first_day_start, starttime)
        first_period_end = min(first_day_end, endtime)
        if first_period_end<=first_period_start:
            first_day_mins=0
        else:
            first_day_sec=first_period_end - first_period_start
            first_day_mins=first_day_sec.seconds/60
        if daycount == 1:
            return first_day_mins
        else:
            last_period_start = days[-1].replace(hour=bus_start_time, minute=0)
            #we know the last day will always start in the bus_start_time

            last_day_end = days[-1].replace(hour=bus_end_time, minute=0)
            last_period_end = min(last_day_end, endtime)
            if last_period_end<=last_period_start:
                last_day_mins=0
            else:
                last_day_sec=last_period_end - last_period_start
                last_day_mins=last_day_sec.seconds/60
            middle_days_mins=0
            if daycount>2:
                middle_days_mins=(daycount-2)*mins_in_working_day
            return first_day_mins + last_day_mins + middle_days_mins


# Calculates the date series with all the business days
# of the period we are interested on
class EnglandAndWalesHolidayCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('New Years Day', month=1, day=1, observance=next_monday),
        GoodFriday,
        EasterMonday,
        Holiday('Early May bank holiday',
                month=5, day=1, offset=DateOffset(weekday=MO(1))),
        Holiday('Spring bank holiday',
                month=5, day=31, offset=DateOffset(weekday=MO(-1))),
        Holiday('Summer bank holiday',
                month=8, day=31, offset=DateOffset(weekday=MO(-1))),
        Holiday('Christmas Day', month=12, day=25, observance=next_monday),
        Holiday('Boxing Day',
                month=12, day=26, observance=next_monday_or_tuesday)
    ]

# From this point its how we use the function



# Here we hardcode a start/end date to create the list of business days
cal = EnglandAndWalesHolidayCalendar()
dayindex = pd.bdate_range(datetime.date(2019,1,1),datetime.date.today(),freq=CDay(calendar=cal))
day_series = dayindex.to_series()


# Convenience function to simplify how we call the main function
# It will take a pre calculated day_series.
def bus_hr(ts_start, ts_end, day_series ):
    BUS_START=8
    BUS_END=20
    minutes = count_mins(ts_start, ts_end, day_series, BUS_START, BUS_END)
    return int(round(minutes/60,0))


# #A set of checks that the function is working properly
# assert bus_hr( pd.Timestamp(2019,9,30,6,1,0) , pd.Timestamp(2019,10,1,9,0,0),day_series) == 13
# assert bus_hr( pd.Timestamp(2019,10,3,10,30,0) , pd.Timestamp(2019,10,3,23,30,0),day_series)==10
# assert bus_hr( pd.Timestamp(2019,8,25,10,30,0) , pd.Timestamp(2019,8,27,10,0,0),day_series) ==2
# assert bus_hr( pd.Timestamp(2019,12,25,8,0,0) , pd.Timestamp(2019,12,25,17,0,0),day_series) ==0
# assert bus_hr( pd.Timestamp(2019,12,26,8,0,0) , pd.Timestamp(2019,12,26,17,0,0),day_series) ==0
# assert bus_hr( pd.Timestamp(2019,12,27,8,0,0) , pd.Timestamp(2019,12,27,17,0,0),day_series) ==9
# assert bus_hr( pd.Timestamp(2019,6,24,5,10,44) , pd.Timestamp(2019,6,24,7,39,17),day_series)==0
# assert bus_hr( pd.Timestamp(2019,6,24,5,10,44) , pd.Timestamp(2019,6,24,8,29,17),day_series)==0
# assert bus_hr( pd.Timestamp(2019,6,24,5,10,44) , pd.Timestamp(2019,6,24,10,0,0),day_series)==2
# assert bus_hr(pd.Timestamp(2019,4,30,21,19,0) , pd.Timestamp(2019,5,1,16,17,56),day_series)==8
# assert bus_hr(pd.Timestamp(2019,4,30,21,19,0) , pd.Timestamp(2019,5,1,20,17,56),day_series)==12
