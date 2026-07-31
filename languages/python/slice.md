# Python 切片 (Slice) 详解

切片是 Python 中用于从序列（字符串、列表、元组等）中提取子序列的强大功能。

## 基本语法
```python
sequence[start:stop:step]
```

## 参数说明
- **start**：起始索引（包含），默认为 0
- **stop**：结束索引（不包含），默认为序列长度
- **step**：步长（间隔），默认为 1

## 1. 基本使用示例
```python
s = "PythonSlice"

# 基本切片
print(s[2:5])      # "tho" - 索引2到4
print(s[:5])       # "Pytho" - 从头到索引4
print(s[6:])       # "Slice" - 索引6到末尾
print(s[:])        # "PythonSlice" - 完整副本
print(s[::2])      # "PtoSle" - 每隔一个字符

# 负索引
print(s[-5:])      # "Slice" - 倒数5个字符
print(s[-8:-3])    # "honSl" - 索引-8到-4
```

## 2. 步长 (step) 的使用
```python
s = "0123456789"

print(s[::1])      # "0123456789" - 正常顺序
print(s[::2])      # "02468" - 偶数位置
print(s[1::2])     # "13579" - 奇数位置
print(s[::-1])     # "9876543210" - 反转
print(s[8:2:-2])   # "864" - 从8到2，步长-2
```

## 3. 不同数据类型的切片
```python
# 列表切片
lst = [0, 1, 2, 3, 4, 5]
print(lst[2:5])     # [2, 3, 4]
print(lst[::-1])    # [5, 4, 3, 2, 1, 0] - 反转列表

# 元组切片
tup = (0, 1, 2, 3, 4, 5)
print(tup[1:4])     # (1, 2, 3)

# 字节切片
bytes_data = b"Python"
print(bytes_data[2:4])  # b'th'
```

## 4. 高级技巧
```python
s = "PythonProgramming"

# 获取前5个和后5个字符
first_5 = s[:5]    # "Pytho"
last_5 = s[-5:]    # "mming"

# 移除首尾字符
without_ends = s[1:-1]  # "ythonProgrammin"

# 提取每第三个字符
every_third = s[::3]  # "Phrrim"

# 反转字符串
reversed_str = s[::-1]  # "gnimmargorPnohtyP"

# 复制列表（浅拷贝）
original = [1, 2, 3, [4, 5]]
copied = original[:]  # 创建新列表，但嵌套列表是引用
copied[3][0] = 999
print(original)  # [1, 2, 3, [999, 5]] - 嵌套列表被修改
```

## 5. 切片赋值（修改原序列）
```python
# 列表切片赋值
lst = [0, 1, 2, 3, 4, 5]
lst[1:4] = [10, 20, 30]  # 替换索引1-3
print(lst)  # [0, 10, 20, 30, 4, 5]

lst[2:5] = [100]  # 替换为单个元素
print(lst)  # [0, 10, 100, 5]

lst[1:3] = []  # 删除元素
print(lst)  # [0, 5]

# 字符串不可变，不支持切片赋值
# s[0:3] = "ABC"  # TypeError
```

## 6. 切片与索引的对应关系
```python
s = "ABCDEFGHIJ"
# 正索引: 0  1  2  3  4  5  6  7  8  9
# 负索引:-10 -9 -8 -7 -6 -5 -4 -3 -2 -1
# 值:    A  B  C  D  E  F  G  H  I  J

print(s[1:8:2])    # "BDFH" - 索引1,3,5,7
print(s[-9:-2:2])  # "BDFH" - 等效的负索引
```

## 7. 常见应用场景
```python
# 1. 回文判断
def is_palindrome(s):
    return s == s[::-1]

# 2. 提取文件名和扩展名
path = "document.txt"
filename = path[:-4]  # "document"
extension = path[-3:]  # "txt"

# 3. 分组处理
data = "abc123def456"
letters = data[::3]  # 每3个取一个: "a1d4"

# 4. 清理字符串
text = "  hello world  "
cleaned = text[1:-1]  # 移除首尾空格（简单示例）

# 5. 逆序输出
for char in "hello"[::-1]:
    print(char)  # o l l e h
```

## 8. 注意事项
```python
s = "Python"

# 切片不会索引越界
print(s[2:100])  # "thon" - 自动截断到末尾
print(s[-100:5]) # "Pytho" - 自动从0开始

# 空切片
print(s[3:2])   # "" - 起始>结束，返回空序列
print(s[2:2])   # "" - 起始=结束，返回空序列

# 步长为负时的注意事项
print(s[5:1:-1])  # "noht" - 包含索引5，不包含索引1
```

切片是 Python 的核心特性之一，掌握它可以让代码更简洁高效。特别适合处理字符串、列表等序列类型的数据操作。