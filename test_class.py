class Surface():
  """docstring for Surface"""
  def __init__(self, arg=[], other=0):
    # super(Surface, self).__init__()
    self.arg = arg
    if other:
      print('yep')

  def out(self):
    print(self.arg)
#     pass
    


class A:
     def __init__(self):
             self.f = Surface()

     def test(self):
             print('yes')

class Person:
 
       # constructor or initializer
      def __init__(self, name): 
            self.name = name # name is data field also commonly known as instance variables
 
      # method which returns a string
      def whoami(self):
           return "You are " + self.name

 
# # p1 = Person('tom') # now we have created a new person object p1
# # print(p1.whoami())
# # print(p1.name)


# B = A()

# # B.test()
# B.f.arg = 7
# # print(B.f)

# def test_func(obj=[]):
# 	print(obj.f.arg)


# test_func(B)