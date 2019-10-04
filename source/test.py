
# CASE 1
# class class_a(object):
#     def __init__(self):
#         self.var_x = 1
#
# class class_b(object):
#     def __init__(self, A):
#         self.var_y = A.var_x
#
# instance_A = class_a()
# print(instance_A.var_x)
# instance_B = class_b(instance_A)
# print(instance_B.var_y)
#
# instance_A.var_x += 10
# print(instance_A.var_x)
# print(instance_B.var_y)



# CASE 2
class class_a(object):
    def __init__(self):
        self.var_x = [1]

class class_b(object):
    def __init__(self, A):
        self.var_y = A.var_x


instance_A = class_a()
print(instance_A.var_x)
instance_B = class_b(instance_A)
print(instance_B.var_y)


instance_A.var_x[0] += 10
print(instance_A.var_x)
print(instance_B.var_y)
