class QuenchFront:
    def __init__(self, x_down, x_up, label):
        self.x_down = x_down
        self.x_up = x_up
        self.label = label

    def to_string(self):
        return "{}: x_down = {}, x_up = {}".format(self.label, self.x_down, self.x_up)

    def check_set_included(self, qf):
        is_x_down_inside = (self.x_down <= qf.x_down) and (self.x_down <= qf.x_up)
        is_x_up_inside = (self.x_up >= qf.x_down) and (self.x_up >= qf.x_up)
        return is_x_down_inside and is_x_up_inside

    def check_overlap(self, qf):
        is_x_down_inside = (self.x_down >= qf.x_down) and (self.x_down <= qf.x_up)
        is_x_up_inside = (self.x_up >= qf.x_down) and (self.x_up <= qf.x_up)
        return is_x_down_inside or is_x_up_inside

    def merge(self, qf):
        x_down_new = min(self.x_down, qf.x_down)
        x_up_new = max(self.x_up, qf.x_up)
        return QuenchFront(x_down_new, x_up_new, self.label+"_"+qf.label)

# test 1
# quenchFronts = [QuenchFront(10.0, 30.0, "1"), QuenchFront(70.0, 80.0, "2"),
#                 QuenchFront(40.0, 50.0, "3"), QuenchFront(20.0, 60.0, "4")]
# test 2
# quenchFronts = [QuenchFront(10.0, 80.0, "1"), QuenchFront(30.0, 60.0, "2"),
#                 QuenchFront(20.0, 70.0, "3"), QuenchFront(40.0, 50.0, "4")]
# test 3
# quenchFronts = [QuenchFront(30.0, 50.0, "1"), QuenchFront(10.0, 70.0, "2"),
#                 QuenchFront(20.0, 60.0, "3"), QuenchFront(40.0, 80.0, "4")]
# test 4 - the same like 3 with 4 next sets equal to the previous ones
quenchFronts = [QuenchFront(30.0, 50.0, "1"), QuenchFront(10.0, 70.0, "2"),
                QuenchFront(20.0, 60.0, "3"), QuenchFront(40.0, 80.0, "4"),
                QuenchFront(30.0, 50.0, "5"), QuenchFront(10.0, 70.0, "6"),
                QuenchFront(20.0, 60.0, "7"), QuenchFront(40.0, 80.0, "8")]

# list sorted with respect to the x_down
quenchFronts_sorted = sorted(quenchFronts, key=lambda QuenchFront: QuenchFront.x_down)
for quench_fronts in quenchFronts_sorted:
    print("label: {}, x_down = {}".format(quench_fronts.label, quench_fronts.x_down))

for qf in quenchFronts_sorted:
    print(qf.to_string())
quenchFrontsMerged = []

index = 0
while index < len(quenchFronts):
    qfOuter = quenchFronts_sorted[index]
    qfMerged = None
    for j in range(index + 1, len(quenchFronts_sorted)):
        qfInner = quenchFronts_sorted[j]
        isOverlap = qfOuter.check_overlap(qfInner)
        isSetIncluded = qfOuter.check_set_included(qfInner)
        to_be_merged = isOverlap or isSetIncluded
        print("Checking overlap of: {} and {}. The result is {}".format(qfOuter.label, qfInner.label, isOverlap))
        if to_be_merged:
            qfMerged = qfOuter.merge(qfInner)
            qfOuter = qfMerged
            index = j + 1

    if qfMerged is None:
        quenchFrontsMerged.append(qfOuter)
        index = index + 1
    else:
        quenchFrontsMerged.append(qfMerged)


print("\nSituation after merging:")
for qfm in quenchFrontsMerged:
    print(qfm.to_string())


