
def merge(list1, list2):
    newlist =[]
    index1 = 0
    index2 = 0

    while index1 < len(list1) and index2 < len(list2):
        if list1[index1] > list2[index2]:
            newlist.append(list2[index2])
            index2 = index2 + 1
        elif list1[index1] < list2[index2]:
            newlist.append(list1[index1])
            index1 = index1 + 1
        elif list1[index1] == list2[index2]:
            newlist.append(list1[index1])
            newlist.append(list2[index2])
            index1 = index1 + 1
            index2 = index2 + 1
    
# add the remainders to the new list
    if index1 < len(list1):
        for item in range(index1, len(list1)):
            newlist.append(list1[item])
    elif index2 < len(list2):
        for item in range(index2, len(list2)):
            newlist.append(list2[item])
    return newlist



item = []
items = [1, 4, 6, 7, 8, 2, 3]
listofitems = []
for n in range(len(items)):
    item = [items[n]]
    listofitems.append(item)
#repeats until there is only one list
while len(listofitems) != 1:
    index = 0
# merge lists
    while index < len(listofitems)-1:
        newlist = merge(listofitems[index], listofitems[index + 1])
        listofitems[index] = newlist
        del listofitems[index + 1]
        index = index + 1 

print(listofitems[0])


