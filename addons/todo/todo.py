import json

class Todo():
    # 创建、删除、写入、读取、修改
    # todo有内容、时间、状态
    def __init__(self):
        self.todo_path = "addons/todo/todo.json"
        self.todo = []
        self.load()

    def load(self):
        with open(self.todo_path, "r") as f:
            self.todo = json.load(f)

    def save(self):
        with open(self.todo_path, "w") as f:
            json.dump(self.todo, f)

    def add(self, content, time):
        self.todo.append({"content": content, "time": time, "status": 0})
        self.save()

    def delete(self, index):
        self.todo.pop(index)
        self.save()

    def finish(self, index):
        self.todo[index-1]["status"] = 1
        self.save()

    def unfinish(self, index):
        self.todo[index]["status"] = 0
        self.save()

    def get(self):
        return self.todo
    
    def get_unfinished(self):
        return [i for i in self.todo if i["status"] == 0]
    
    def get_finished(self):
        return [i for i in self.todo if i["status"] == 1]
    
    def get_by_index(self, index):
        return self.todo[index]
    
    def get_by_status(self, status):
        return [i for i in self.todo if i["status"] == status]
    
    def get_by_time(self, time):
        return [i for i in self.todo if i["time"].startswith(time)]
