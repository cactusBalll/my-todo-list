import os
import pickle
#print (os.environ)
#print (os.path.expandvars('$HOME'))
print (os.path.expanduser('~'))
print(os.name)
class A():
    def __init__(self) -> None:
        self.l = [1,2,3]
    def say(self):
        print(self.l)

with open("s.bin","wb") as f:
    pickle.dump(A(), f)

with open("s.bin","rb") as f:
    o = pickle.load(f)
    print(isinstance(o,A))
    print(type(A()))
    o.say()