import datetime


class YardCrane:
    def __init__(self):
        self.name = str()
        self.bus_indx = int()
        self.max_power = float()
        self.job_plan = list()
        self.baseload_profile = dict()
        self.jobs_sorted = dict()

    def extract_data_from_dict(self, yc_dict):
        self.name = yc_dict['Name']
        self.bus_indx = yc_dict['Bus index in electrical network']
        self.max_power = yc_dict['Maximum power']

    def compute_yc_baseload_profile(self, time_intervals):
        jobs_in_each_hour = dict()
        for t in time_intervals:
            jobs_in_hour_list = []  # List of all jobs that are performed during timestep t
            baseload = 0
            for job in self.job_plan:
                start = job.start
                end = job.end
                if (start >= t) and (end < t + datetime.timedelta(hours=1)):
                    jobs_in_hour_list.append(job)
                    baseload += job.energy
                elif (start < t) and (end >= t + datetime.timedelta(hours=1)):
                    jobs_in_hour_list.append(job)
                    duration = end - start
                    coeff = (24 * 60 * 60) / duration.seconds
                    baseload += job.energy * coeff
                elif (start < t + datetime.timedelta(hours=1)) and (end >= t + datetime.timedelta(hours=1)):
                    jobs_in_hour_list.append(job)
                    duration_current_time_step = t + datetime.timedelta(hours=1) - start
                    coeff = duration_current_time_step.seconds / (24 * 60 * 60)
                    baseload += job.energy * coeff
                elif (end >= t) and (start < t):
                    jobs_in_hour_list.append(job)
                    duration_current_time_step = end - t
                    coeff = duration_current_time_step.seconds / (24 * 60 * 60)
                    baseload += job.energy * coeff
            jobs_in_each_hour[t] = sorted(jobs_in_hour_list, key=lambda x: x.start, reverse=False)
            self.baseload_profile[t] = baseload
        # Add index of each job
        indx = 1
        for timestep in jobs_in_each_hour:
            for job in jobs_in_each_hour[timestep]:
                job.name = f'Job {indx} (Crane {self.name})'
                indx += 1
            if len(jobs_in_each_hour[timestep]) != 0:
                indx += 1
        self.jobs_sorted = jobs_in_each_hour


class YCJob:
    def __init__(self):
        self.type = str()
        self.energy = float()
        self.start = float()
        self.end = float()

    def extract_data_from_dict(self, job_dict):
        self.type = job_dict['Type of action']
        self.energy = job_dict['Energy']
        self.start = job_dict['Start']
        self.end = job_dict['End']


job_plan_example = {'YC 1': [{'Start': datetime.datetime(2022, 1, 20, 10, 0, 0),
                              'End': datetime.datetime(2022, 1, 20, 10, 2, 0),
                              'Energy up': 2,
                              'Energy move': 0,
                              'Energy down': -1.8},
                             {'Start': datetime.datetime(2022, 1, 20, 10, 2, 0),
                              'End': datetime.datetime(2022, 1, 20, 10, 5, 0),
                              'Energy up': 2.5,
                              'Energy move': 0,
                              'Energy down': -2},
                             {'Start': datetime.datetime(2022, 1, 20, 10, 5, 0),
                              'End': datetime.datetime(2022, 1, 20, 10, 10, 0),
                              'Energy up': 4,
                              'Energy move': 0,
                              'Energy down': -3.8}],
                    'YC 2': [{'Start': datetime.datetime(2022, 1, 20, 10, 0, 0),
                              'End': datetime.datetime(2022, 1, 20, 10, 2, 0),
                              'Energy up': 2,
                              'Energy move': 0,
                              'Energy down': -1.8},
                             {'Start': datetime.datetime(2022, 1, 20, 10, 2, 0),
                              'End': datetime.datetime(2022, 1, 20, 10, 5, 0),
                              'Energy up': 2.5,
                              'Energy move': 0,
                              'Energy down': -2},
                             {'Start': datetime.datetime(2022, 1, 20, 10, 5, 0),
                              'End': datetime.datetime(2022, 1, 20, 10, 10, 0),
                              'Energy up': 4,
                              'Energy move': 0,
                              'Energy down': -3.8}]
                    }
