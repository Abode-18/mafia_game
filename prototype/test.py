import uuid
l1=[str(uuid.uuid4()),str(uuid.uuid4()),str(uuid.uuid4())]
l2 = [l1[-1],l1[-2],l1[-3]]

print(sorted(l1) == sorted(l2))