import pickle
import socket
import time
from tkinter import messagebox, ttk
from tkinter import *
from tkcalendar import *

# Todo list classes
class TODO_ITEM():
    def __init__(self, task, member, due_date, task_id):
        self.task = task
        self.member = member
        self.due_date = due_date
        self.finished = False
        # self.sub_tasks = []
        self.task_id = task_id
    
    # def add_subtask(self, task):
    #     self.sub_tasks.append(task)


class TODO_LIST():
    def __init__(self):
        self.todo_list = {}
        self.occupied_dates = {}

    def add_task(self, task):
        self.todo_list[task.task_id] = task
        self.occupied_dates[task.due_date] = True
    
    # def item_add_subtask(self, sub_task, task_id):
    #     task_id = int(task_id)
    #     self.todo_list[task_id].add_subtask(sub_task)
    #     self.occupied_dates[task_id] = True
    
    def delete_task(self, del_task_id):
        del_task_id = int(del_task_id)
        del self.todo_list[del_task_id]
        self.occupied_dates[del_task_id] = False



# Instantiate tkinter object
root = Tk()
root.title('My ToDo List')
root.geometry('600x500')
count = 0
todo_list = TODO_LIST()



# Connection
host = socket.gethostname()
port = 8088
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))




# Util function
def add_single_task(task, member, due_date, task_finished, parent):
    global count
    todo_item = TODO_ITEM(task=task, member=member, due_date=due_date, task_id=count)
    todo_item.finished = task_finished
    todo_list.add_task(todo_item)
    finished = 'YES' if task_finished == True else 'NOPE'
    my_tree.insert(parent=parent, index='end', iid=count, text='Task', values=(todo_item.task, todo_item.member, todo_item.due_date, finished))
    count += 1



# Select function
def select(e):
    task_input.delete(0, END)
    member_input.delete(0, END)
    date_input.delete(0, END)
    current_task = my_tree.focus()
    values = my_tree.item(current_task, 'values')
    task_input.insert(0, values[0])
    member_input.insert(0, values[1])
    date_input.insert(0, values[2])

def double_click(e):
    selected_task = my_tree.focus()
    selected_finished = my_tree.item(selected_task, 'values')[3]
    finished = 'YES' if selected_finished == 'NOPE' else 'NOPE'
    todo_list.todo_list[int(selected_task)].finished = True if finished == 'YES' else False
    my_tree.item(selected_task, text='Task', values=(task_input.get(), member_input.get(), date_input.get(), finished))



# Button functions
def add_task():
    task = task_input.get()
    member = member_input.get()
    due_date = str(date_input.get_date())
    if member == 'shared':
        print(todo_list.occupied_dates.keys())
        if due_date not in todo_list.occupied_dates.keys():
            add_single_task(task=task, member=member, due_date=due_date, task_finished=False, parent='')
        else:
            messagebox.showwarning(title='Warning', message='Date already occupied!')
    else:
        add_single_task(task=task, member=member, due_date=due_date, task_finished=False, parent='')

def edit_task():
    current_task = my_tree.focus()
    current_task_text = my_tree.item(current_task, 'text')
    current_task_finished = my_tree.item(current_task, 'values')[3]
    new_task = task_input.get()
    new_member = member_input.get()
    new_due_date = date_input.get_date()
    todo_list.todo_list[int(current_task)].task = new_task
    todo_list.todo_list[int(current_task)].member = new_member
    todo_list.todo_list[int(current_task)].due_date = new_due_date
    my_tree.item(current_task, text=current_task_text, values=(new_task, new_member, new_due_date, current_task_finished))
    task_input.delete(0, END)
    member_input.delete(0, END)
    date_input.delete(0, END)

def delete_task():
    global count
    selected_tasks = my_tree.selection()
    if selected_tasks:
        for task in selected_tasks:
            my_tree.delete(task)
            todo_list.delete_task(task)
    else:
        messagebox.showwarning(title='Warning', message='No selected tasks!')

def save_task():
    with open('local_tasks1.pkl', "wb") as f:
        pickle.dump(todo_list, f)
    s.send("save".encode('utf-8'))
    time.sleep(1)
    
    with open('local_tasks1.pkl', 'rb') as file1:
        i = 0
        for line in file1:
            i += 1
        s.send(str(i).encode('utf-8'))
        time.sleep(1)

    with open('local_tasks1.pkl', "rb") as file1:
        for line in file1:
            s.send(line)
            time.sleep(1)

def load_tasks():
    s.send("load".encode('utf-8'))
    time.sleep(1)
    with open('local_tasks1.pkl', 'wb') as file:
        count_line = int(s.recv(1024))
        for i in range(count_line):
            d = s.recv(1024)
            file.write(d)
        print("server_save")
        
    with open('local_tasks1.pkl', 'rb') as f:
        server_todo_list = pickle.load(f)
    for task_id in server_todo_list.todo_list.keys():
        todo_item = server_todo_list.todo_list[task_id]
        task = todo_item.task
        member = todo_item.member
        due_date = todo_item.due_date
        task_finished = todo_item.finished
        add_single_task(task=task, member=member, due_date=due_date, task_finished=task_finished, parent='')



# Add style
style = ttk.Style()
style.theme_use('clam')
style.configure('Treeview', background='#f5f5f5', foreground='black', rowheight=25, fieldbackbground='silver')
style.map('Treeview', background=[('selected', 'green')])



# Add frame
frame_tasks = Frame(root)
frame_tasks.pack()

frame_ui = Frame(root)
frame_ui.pack()

frame_buttons = Frame(root)
frame_buttons.pack(pady=20)



# Tasks scrollbar
tasks_scroll = Scrollbar(frame_tasks)
tasks_scroll.pack(side=RIGHT, fill=Y)



# Add treeview and corresponding settings
my_tree = ttk.Treeview(frame_tasks, height=12, selectmode='extended', yscrollcommand=tasks_scroll.set)

my_tree['columns'] = ('Task', 'Member', 'Due Date', 'Finished') 
my_tree.column("#0", width=0, minwidth=0)
my_tree.column('Task', anchor=CENTER, width=120)
my_tree.column('Member', anchor=CENTER, width=120)
my_tree.column('Due Date', anchor=CENTER, width=120)
my_tree.column('Finished', anchor=CENTER, width=120)

# Create headings
my_tree.heading("#0", text='', anchor=W)
my_tree.heading('Task', text='Task', anchor=CENTER)
my_tree.heading('Member', text='Member', anchor=CENTER)
my_tree.heading('Due Date', text='Due Date', anchor=CENTER)
my_tree.heading('Finished', text='Finished', anchor=CENTER)

my_tree.bind("<ButtonRelease-1>", select)
my_tree.bind("<Double-Button-1>", double_click)

my_tree.pack()

# Configure scrollbar
tasks_scroll.config(command=my_tree.yview)



# Input box labels
task_label = Label(frame_ui, text='Task')
task_label.grid(row=0, column=0)

member_label = Label(frame_ui, text='Member')
member_label.grid(row=0, column=1)

date_label = Label(frame_ui, text='Due Date')
date_label.grid(row=0, column=2)



# Input boxes
task_input = Entry(frame_ui)
task_input.grid(row=1, column=0)

member_input = Entry(frame_ui)
member_input.grid(row=1, column=1)  

date_input = DateEntry(frame_ui, selectmode='day', date_pattern='yyyy/MM/dd')
date_input.grid(row=1, column=2)



# Create buttons
add_button = Button(frame_buttons, text='Add Task', width=10, command=add_task)
add_button.grid(row=1, column=0)

edit_button = Button(frame_buttons, text='Edit Task', width=8, command=edit_task)
edit_button.grid(row=1, column=2)

delete_button = Button(frame_buttons, text='Delete Task', width=8, command=delete_task)
delete_button.grid(row=1, column=3)

save_button = Button(frame_buttons, text='Save Tasks', width=8, command=save_task)
save_button.grid(row=1, column=4)

load_button = Button(frame_buttons, text='Load Tasks', width=8, command=load_tasks)
load_button.grid(row=1, column=5)



if __name__ == '__main__':
    root.mainloop()