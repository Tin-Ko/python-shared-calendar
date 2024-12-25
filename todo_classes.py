

class TODO_ITEM():
    def __init__(self, task, member, due_date, task_id):
        self.task = task
        self.member = member
        self.due_date = due_date
        self.finished = False
        self.sub_tasks = []
        self.task_id = task_id
    
    def add_subtask(self, task):
        self.sub_tasks.append(task)


class TODO_LIST():
    def __init__(self):
        self.todo_list = {}
        self.occupied_dates = {}

    def add_task(self, task):
        self.todo_list[task.task_id] = task
        self.occupied_dates[task.due_date] = True
    
    def item_add_subtask(self, sub_task, task_id):
        task_id = int(task_id)
        self.todo_list[task_id].add_subtask(sub_task)
        self.occupied_dates[task_id] = True
    
    def delete_task(self, del_task):
        del self.todo_list[del_task.task_id]
        print('deleted')
        self.occupied_dates[del_task.task_id] = False
