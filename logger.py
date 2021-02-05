from sys import stdout
import time
import threading
import queue


class Logger:
    DELIMITER = '-' * 60

    def __init__(self, items_list=None, progress_bar_length=20):
        self.items_list = items_list
        self.log_path = queue.Queue()
        self.progress_bar_length = progress_bar_length
        self.t0 = time.perf_counter()
        self.t_est = ''
        if items_list is not None:
            self.last_record = queue.Queue()
            self.last = threading.Thread(target=self.print_progress_bar, args=(self.progress_bar_length,), daemon=True)
            self.last.start()

    def __repr__(self):
        return f'Logger(items_list={self.items_list}, progress_bar_length={self.progress_bar_length})'

    def log(self, item, thread_id=0):
        log_item = str(item).replace('\n', ' ')
        self.log_path.put({thread_id: log_item})
        if self.items_list is not None:
            self.last_record.put(f'Thread-{thread_id} | {log_item}')

    def item_processed(self, thread_id=0):
        self.log(self.DELIMITER, thread_id)

    def itemize_logs(self):
        log_dict = {}
        while not self.log_path.empty():
            item = self.log_path.get()
            self.log_path.task_done()
            if 'Logger working time' in item:
                log_dict['WorkTime'] = item
            else:
                key = int(str(item.keys()).replace('dict_keys([', '').replace('])', ''))
                value = [str(item.values()).replace('dict_values([', '').replace('])', '')]
                if key in log_dict.keys():
                    log_dict[key] += value
                else:
                    log_dict[key] = value
        return log_dict

    @staticmethod
    def print_logs_to_console(log_dict):
        for k, v in log_dict.items():
            if k != 'WorkTime':
                print('*' * 60)
                print(f'Thread {k}')
                print('*' * 60)
                for record in v:
                    if record.isdigit():
                        print(record)
                    else:
                        print(record[1:-1])
                print('')
            else:
                print(v)

    @staticmethod
    def write_logs_to_txt(log_dict):
        print('Writing to txt...')
        with open('log.txt', 'w') as file:
            for k, v in log_dict.items():
                if k != 'WorkTime':
                    file.write('*' * 60 + '\n')
                    file.write(f'Thread {k}' + '\n')
                    file.write('*' * 60 + '\n')
                    for record in v:
                        if record.isdigit():
                            file.write(record + '\n')
                        else:
                            file.write(record[1:-1] + '\n')
                    file.write('' + '\n')
                else:
                    file.write(v + '\n')
        print('Written to txt')

    @staticmethod
    def convert_seconds(seconds):
        seconds = round(seconds)
        if seconds < 60:
            return f'{seconds} sec'
        elif 60 <= seconds < 3600:
            minutes = seconds // 60
            seconds -= minutes * 60
            seconds = seconds if seconds >= 10 else str(0) + str(seconds)
            return f'{minutes}:{seconds} min'
        elif seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds - hours * 3600) // 60
            seconds -= (hours * 3600 + minutes * 60)
            minutes = minutes if minutes >= 10 else str(0) + str(minutes)
            seconds = seconds if seconds >= 10 else str(0) + str(seconds)
            return f'{hours}:{minutes}:{seconds} h'

    def end_logging(self, log_to_txt=False, log_to_console=True):
        t1 = time.perf_counter()
        self.log_path.put(f'Logger working time: {self.convert_seconds(t1 - self.t0)}')
        log_dict = self.itemize_logs()
        if self.items_list is not None:
            self.last_record.join()
        if log_to_console:
            self.print_logs_to_console(log_dict)
        if log_to_txt:
            self.write_logs_to_txt(log_dict)

    def print_progress_bar(self, bar_length):
        counter = 0
        progress_usual = '\r{}{}| {:.0f}% | {}/{} items processed | {} || {}'
        progress_usual_short = '\r{}{}| {:.0f}% | {}/{} items processed | {} || {}...'
        progress_end = '\r{}{}| {:.0f}% | {}/{} items processed | {} || {}\n\n'
        progress_end_short = '\r{}{}| {:.0f}% | {}/{} items processed | {} || {}...\n\n'
        limit = 150
        while True:
            last_record = self.last_record.get()
            self.last_record.task_done()
            if self.DELIMITER in last_record:
                counter += 1
                time_left = self.convert_seconds((time.perf_counter() - self.t0) * (len(self.items_list) / counter - 1))
                self.t_est = f'Estimated time left: {time_left} '
            if counter != len(self.items_list):
                if len(last_record) <= limit:
                    stdout.write(progress_usual.format(
                        '█' * int(counter / len(self.items_list) * bar_length),
                        '-' * int((1 - counter / len(self.items_list)) * bar_length),
                        counter / len(self.items_list) * 100,
                        counter,
                        len(self.items_list),
                        self.t_est,
                        last_record.replace(self.DELIMITER, 'Item processed')
                    ))
                else:
                    stdout.write(progress_usual_short.format(
                        '█' * int(counter / len(self.items_list) * bar_length),
                        '-' * int((1 - counter / len(self.items_list)) * bar_length),
                        counter / len(self.items_list) * 100,
                        counter,
                        len(self.items_list),
                        self.t_est,
                        last_record[:100].replace(self.DELIMITER, 'Item processed')
                    ))
            else:
                if len(last_record) <= limit:
                    stdout.write(progress_end.format(
                        '█' * int(counter / len(self.items_list) * bar_length),
                        '-' * int((1 - counter / len(self.items_list)) * bar_length),
                        counter / len(self.items_list) * 100,
                        counter,
                        len(self.items_list),
                        self.t_est,
                        last_record.replace(self.DELIMITER, 'Item processed')
                    ))
                else:
                    stdout.write(progress_end_short.format(
                        '█' * int(counter / len(self.items_list) * bar_length),
                        '-' * int((1 - counter / len(self.items_list)) * bar_length),
                        counter / len(self.items_list) * 100,
                        counter,
                        len(self.items_list),
                        self.t_est,
                        last_record[:100].replace(self.DELIMITER, 'Item processed')
                    ))
