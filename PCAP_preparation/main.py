from sys import path
path.insert(0,'e:\\code\\LearningPython\\PCAP_preparation\\modules')
path.insert(1,'e:\\code\\LearningPython\\PCAP_preparation\\packages')
# for p in path:
#     print(p)
from module import suml, prodl

zeroes = [0 for i in range(5)]
ones = [1 for i in range(5)]
print(suml(zeroes))
print(prodl(ones))


