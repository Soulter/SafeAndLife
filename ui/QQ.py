class QQ:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def qq(self):
        print("qq")

    def __str__(self):
        return "name = %s, age = %d" % (self.name, self.age)