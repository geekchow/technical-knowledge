---
title: "解释 python3 的 threading.Semaphore 机制"
author:
published:
created: 2026-04-06
description: "腾讯文档-智能文档"
tags:
  - "clippings"
---

# 解释 python3 的 threading.Semaphore 机制

解释 python3 的 threading.Semaphore 机制

Recently saved 16:28

Add icon

Add cover

Page settings

用户:

解释 python3 的 threading.Semaphore 机制

元宝:

threading.Semaphore 是 Python 中用于控制并发线程数量的同步原语，基于操作系统的信号量机制实现。以下是核心机制解析：

信号量计数器：初始化时设定一个整数值（默认为1），表示可同时访问共享资源的线程数量。

P/V 操作：

acquire()：计数器减1（P操作），若计数器为0则线程阻塞等待。

release()：计数器加1（V操作），并唤醒一个等待线程。

12345678910111213141516171819

import threading # 初始化信号量，允许最多3个线程同时访问 sem = threading.Semaphore(value=3) def task(): sem.acquire() # 计数器-1（若计数器=0则阻塞） try: # 访问共享资源 print(f"{threading.current\_thread().name} 正在工作...") finally: sem.release() # 计数器+1，唤醒等待线程 # 创建多个线程测试 threads = \[threading.Thread(target=task) for \_ in range(5)\] for t in threads: t.start() for t in threads: t.join()

可重入性：标准 Semaphore 不可重入（同一线程重复调用 acquire() 会导致死锁），需用 threading.BoundedSemaphore 防止过度释放。

超时机制：acquire(timeout=5) 支持超时等待。

公平性：默认无严格线程唤醒顺序，依赖操作系统调度。

| 同步原语 | 并发数 | 重入性 | 典型场景 |
| --- | --- | --- | --- |
| Lock | 1 | 不可重入 | 互斥访问 |
| RLock | 1 | 同一线程可重入 | 嵌套锁 |
| Semaphore(n) | n | 不可重入 | 连接池/限流 |

资源池管理（如数据库连接池限制）

限流控制（限制并发请求数）

生产者-消费者模型（通过二进制信号量同步）

1234567

\# 错误示例：过度释放会虚假增加计数器 sem = threading.Semaphore(1) sem.release() # 计数器变为2，超出初始限制！ # 建议使用 BoundedSemaphore 防止异常释放 bounded\_sem = threading.BoundedSemaphore(1) bounded\_sem.release() # 抛出 ValueError: Semaphore released too many times

通过合理控制 acquire()/release() 的调用，信号量可有效平衡线程并发与资源保护，是复杂线程协作的基础工具之一。

用户:

import threading

class FooBar:

1

def \_\_init\_\_(self, n): self.n = n self.foo = threading.Lock() self.bar = threading.Lock() self.bar.acquire() def foo(self, printFoo: 'Callable\[\[\], None\]') -> None: for i in range(self.n): self.foo.acquire() # printFoo() outputs "foo". Do not change or remove this line. printFoo() self.bar.release() def bar(self, printBar: 'Callable\[\[\], None\]') -> None: for i in range(self.n): self.bar.aquire() # printBar() outputs "bar". Do not change or remove this line. printBar() self.foo.release()

fb = FooBar(3)

result = \[\]

t1 = threading.Thread(target=fb.foo, args=\[lambda: result.append("foo")\])

t2 = threading.Thread(target=fb.bar, args=\[lambda: result.append("bar")\])

t1.start(); t2.start()

t1.join(); t2.join()

print("".join(result)) # foobarfoobarfoobar ✅

Traceback (most recent call last):

File "/opt/homebrew/Cellar/python@3.14/3.14.3\_1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/threading.py", line 1082, in \_bootstrap\_inner

1

self.\_context.run(self.run) ~~~~~~~~~~~~~~~~~^^^^^^^^^^

File "/opt/homebrew/Cellar/python@3.14/3.14.3\_1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/threading.py", line 1082, in \_bootstrap\_inner

1

self.\_context.run(self.run) ~~~~~~~~~~~~~~~~~^^^^^^^^^^

File "/opt/homebrew/Cellar/python@3.14/3.14.3\_1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/threading.py", line 1024, in run

1

self.\_target(\*self.\_args, \*\*self.\_kwargs) ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

File "/opt/homebrew/Cellar/python@3.14/3.14.3\_1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/threading.py", line 1024, in run

1

self.\_target(\*self.\_args, \*\*self.\_kwargs) ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TypeError: '\_thread.lock' object is not callable

TypeError: '\_thread.lock' object is not callable

元宝:

你的代码有两个关键错误：

1.

属性名冲突：foo 属性被同时用作锁和方法名

2.

拼写错误：aquire() 应该是 acquire()

以下是修正后的代码：

12345678910111213141516171819202122232425262728293031

import threading class FooBar: def \_\_init\_\_(self, n): self.n = n self.foo\_lock = threading.Lock() # 重命名为 foo\_lock self.bar\_lock = threading.Lock() # 重命名为 bar\_lock self.bar\_lock.acquire() # 先锁住 bar，让 foo 先执行 def foo(self, printFoo) -> None: for i in range(self.n): self.foo\_lock.acquire() # 获取 foo 锁 printFoo() self.bar\_lock.release() # 释放 bar 锁 def bar(self, printBar) -> None: for i in range(self.n): self.bar\_lock.acquire() # 获取 bar 锁，修正拼写 printBar() self.foo\_lock.release() # 释放 foo 锁 fb = FooBar(3) result = \[\] t1 = threading.Thread(target=fb.foo, args=\[lambda: result.append("foo")\]) t2 = threading.Thread(target=fb.bar, args=\[lambda: result.append("bar")\]) t1.start(); t2.start() t1.join(); t2.join() print("".join(result)) # 输出: foobarfoobarfoobar ✅

错误原因解析：

1.

属性名冲突：

123456

def \_\_init\_\_(self, n): self.foo = threading.Lock() # 这里定义了 foo 为 Lock 对象 #... def foo(self, printFoo): # 这里又定义了 foo 为方法 #...

当调用 fb.foo 时，Python 找到的是 Lock 对象而不是方法，导致 'lock' object is not callable 错误。

2.

拼写错误：aquire() → acquire()

运行逻辑说明：

1.

开始时，foo\_lock 是解锁状态，bar\_lock 是上锁状态

2.

foo() 先获取 foo\_lock，打印 "foo"，然后释放 bar\_lock

3.

bar() 获取 bar\_lock，打印 "bar"，然后释放 foo\_lock

4.

循环 n 次，确保交替输出 "foo" 和 "bar"

用户:

找最长回文

class Solution:

1

def longestPalindrome(self, s: str) -> str: sl = list(s) huiwen = "" # find all window = 2 for i in range(0, len(s), 1): while i + window < len(s): if sl\[i: i + window\] == sl\[i: i + window\].reverse(): if window > len(huiwen): huiwen = sl\[i: i + window\] window += 1 window = 2 return huiwen

元宝:

你的代码存在几个问题：

1.

逻辑错误：窗口大小应该从当前字符开始向外扩展，而不是固定从2开始

2.

reverse() 用法错误：reverse() 是原地反转，不返回新列表

3.

窗口更新逻辑错误：每次外层循环重置窗口，无法找到更长的回文

4.

边界判断错误：while 循环条件有问题

以下是修正后的中心扩展法实现（推荐方法，O(n²) 时间复杂度）：

1234567891011121314151617181920212223242526

class Solution: def longestPalindrome(self, s: str) -> str: if not s: return "" def expand\_around\_center(left: int, right: int) -> str: """从中心向两边扩展，返回最长回文""" while left >= 0 and right < len(s) and s\[left\] == s\[right\]: left -= 1 right += 1 return s\[left + 1:right\] # 注意要回退到有效位置 longest = s\[0\] for i in range(len(s)): # 奇数长度回文（中心为单个字符） odd\_pal = expand\_around\_center(i, i) if len(odd\_pal) > len(longest): longest = odd\_pal # 偶数长度回文（中心为两个相同字符） even\_pal = expand\_around\_center(i, i + 1) if len(even\_pal) > len(longest): longest = even\_pal return longest

用法示例：

1234

sol = Solution() print(sol.longestPalindrome("babad")) # 输出: "bab" 或 "aba" print(sol.longestPalindrome("cbbd")) # 输出: "bb" print(sol.longestPalindrome("a")) # 输出: "a"

如果你想保持滑动窗口的思路，修正后的版本如下（效率较低，O(n³)）：

1234567891011121314151617

class Solution: def longestPalindrome(self, s: str) -> str: n = len(s) if n < 2: return s longest = s\[0\] # 检查所有可能的子串 for i in range(n): for window in range(i + 1, n + 1): # window 表示子串结束位置 sub = s\[i:window\] if sub == sub\[::-1\]: # 使用切片反转 if len(sub) > len(longest): longest = sub return longest

主要修正点：

1.

使用切片 \[::-1\] 反转字符串，而不是 reverse() 方法

2.

正确嵌套循环：外层循环遍历起始位置，内层循环遍历结束位置

3.

从最小的窗口（长度2）开始，逐渐扩大

4.

处理空字符串和单字符的特殊情况

推荐使用中心扩展法，因为它的时间复杂度是 O(n²)，而滑动窗口版本是 O(n³)，在大字符串上效率较低。

用户:

python slice

元宝:

切片是 Python 中用于从序列（字符串、列表、元组等）中提取子序列的强大功能。

1

sequence\[start:stop:step\]

start：起始索引（包含），默认为 0

stop：结束索引（不包含），默认为序列长度

step：步长（间隔），默认为 1

123456789101112

s = "PythonSlice" # 基本切片 print(s\[2:5\]) # "tho" - 索引2到4 print(s\[:5\]) # "Pytho" - 从头到索引4 print(s\[6:\]) # "Slice" - 索引6到末尾 print(s\[:\]) # "PythonSlice" - 完整副本 print(s\[::2\]) # "PtoSle" - 每隔一个字符 # 负索引 print(s\[-5:\]) # "Slice" - 倒数5个字符 print(s\[-8:-3\]) # "honSl" - 索引-8到-4

1234567

s = "0123456789" print(s\[::1\]) # "0123456789" - 正常顺序 print(s\[::2\]) # "02468" - 偶数位置 print(s\[1::2\]) # "13579" - 奇数位置 print(s\[::-1\]) # "9876543210" - 反转 print(s\[8:2:-2\]) # "864" - 从8到2，步长-2

3\. 不同数据类型的切片

123456789101112

\# 列表切片 lst = \[0, 1, 2, 3, 4, 5\] print(lst\[2:5\]) # \[2, 3, 4\] print(lst\[::-1\]) # \[5, 4, 3, 2, 1, 0\] - 反转列表 # 元组切片 tup = (0, 1, 2, 3, 4, 5) print(tup\[1:4\]) # (1, 2, 3) # 字节切片 bytes\_data = b"Python" print(bytes\_data\[2:4\]) # b'th'

1234567891011121314151617181920

s = "PythonProgramming" # 获取前5个和后5个字符 first\_5 = s\[:5\] # "Pytho" last\_5 = s\[-5:\] # "mming" # 移除首尾字符 without\_ends = s\[1:-1\] # "ythonProgrammin" # 提取每第三个字符 every\_third = s\[::3\] # "Phrrim" # 反转字符串 reversed\_str = s\[::-1\] # "gnimmargorPnohtyP" # 复制列表（浅拷贝） original = \[1, 2, 3, \[4, 5\]\] copied = original\[:\] # 创建新列表，但嵌套列表是引用 copied\[3\]\[0\] = 999 print(original) # \[1, 2, 3, \[999, 5\]\] - 嵌套列表被修改

5\. 切片赋值（修改原序列）

12345678910111213

\# 列表切片赋值 lst = \[0, 1, 2, 3, 4, 5\] lst\[1:4\] = \[10, 20, 30\] # 替换索引1-3 print(lst) # \[0, 10, 20, 30, 4, 5\] lst\[2:5\] = \[100\] # 替换为单个元素 print(lst) # \[0, 10, 100, 5\] lst\[1:3\] = \[\] # 删除元素 print(lst) # \[0, 5\] # 字符串不可变，不支持切片赋值 # s\[0:3\] = "ABC" # TypeError

6\. 切片与索引的对应关系

1234567

s = "ABCDEFGHIJ" # 正索引: 0 1 2 3 4 5 6 7 8 9 # 负索引:-10 -9 -8 -7 -6 -5 -4 -3 -2 -1 # 值: A B C D E F G H I J print(s\[1:8:2\]) # "BDFH" - 索引1,3,5,7 print(s\[-9:-2:2\]) # "BDFH" - 等效的负索引

1234567891011121314151617181920

\# 1. 回文判断 def is\_palindrome(s): return s == s\[::-1\] # 2. 提取文件名和扩展名 path = "document.txt" filename = path\[:-4\] # "document" extension = path\[-3:\] # "txt" # 3. 分组处理 data = "abc123def456" letters = data\[::3\] # 每3个取一个: "a1d4" # 4. 清理字符串 text = " hello world " cleaned = text\[1:-1\] # 移除首尾空格（简单示例） # 5. 逆序输出 for char in "hello"\[::-1\]: print(char) # o l l e h

123456789101112

s = "Python" # 切片不会索引越界 print(s\[2:100\]) # "thon" - 自动截断到末尾 print(s\[-100:5\]) # "Pytho" - 自动从0开始 # 空切片 print(s\[3:2\]) # "" - 起始>结束，返回空序列 print(s\[2:2\]) # "" - 起始=结束，返回空序列 # 步长为负时的注意事项 print(s\[5:1:-1\]) # "noht" - 包含索引5，不包含索引1

切片是 Python 的核心特性之一，掌握它可以让代码更简洁高效。特别适合处理字符串、列表等序列类型的数据操作。

用户:

z字型变换

class Solution:

1

def convert(self, s: str, numRows: int) -> str: n = len(s) if numRows == 1: return s row = 0 col = 0 cur = 0 numCol = int(n / numRows -1) +1 matrix = \[ \['' for \_ in range(n) \] for \_ in range(numRows)\] while cur < n: if row < numRows: matrix\[row\]\[col\] = s\[cur\] row += 1 cur += 1 else: # z back while row > 0 and cur < n: matrix\[row\]\[col\] = s\[cur\] row -= 1 col += 1 cur += 1 lines = \[''.join(x) for x in matrix\] one\_line = ''.join(lines) return one\_line

元宝:

你的代码有几个关键问题：

1.

列数计算错误：numCol 计算不准确

2.

索引越界：当 row = numRows 时访问 matrix\[row\] 会越界

3.

逻辑错误："Z" 字形回折部分的列坐标和行坐标更新有问题

4.

矩阵初始过大：列数使用 n 太大，效率低

以下是修正后的代码：

123456789101112131415161718192021

class Solution: def convert(self, s: str, numRows: int) -> str: if numRows == 1 or numRows >= len(s): return s # 创建行数组，每行存储对应字符 rows = \[''\] \* numRows cur\_row = 0 going\_down = False # 方向标志 for char in s: rows\[cur\_row\] += char # 到达边界时改变方向 if cur\_row == 0 or cur\_row == numRows - 1: going\_down = not going\_down # 更新行号 cur\_row += 1 if going\_down else -1 return ''.join(rows)

123456789101112131415161718192021222324252627282930313233343536373839404142434445464748

class Solution: def convert(self, s: str, numRows: int) -> str: n = len(s) if numRows == 1 or numRows >= n: return s # 计算需要的列数 # 每个周期包含：向下 numRows 列 + 斜向上 numRows-2 列 cycle\_len = 2 \* numRows - 2 cycles = (n + cycle\_len - 1) // cycle\_len # 向上取整 numCols = cycles \* (numRows - 1) # 每周期占 numRows-1 列 # 创建矩阵 matrix = \[\['' for \_ in range(numCols)\] for \_ in range(numRows)\] row, col = 0, 0 cur = 0 going\_down = True while cur < n: matrix\[row\]\[col\] = s\[cur\] cur += 1 if going\_down: if row < numRows - 1: row += 1 else: # 转向斜向上 going\_down = False row -= 1 col += 1 else: if row > 0: row -= 1 col += 1 else: # 转向向下 going\_down = True row += 1 # 按行读取 result = '' for i in range(numRows): for j in range(numCols): if matrix\[i\]\[j\]: result += matrix\[i\]\[j\] return result

12345678910111213141516171819

class Solution: def convert(self, s: str, numRows: int) -> str: if numRows == 1 or numRows >= len(s): return s result = \[\] cycle\_len = 2 \* numRows - 2 for i in range(numRows): for j in range(i, len(s), cycle\_len): result.append(s\[j\]) # 中间行有额外的字符 if i!= 0 and i!= numRows - 1: k = j + cycle\_len - 2 \* i if k < len(s): result.append(s\[k\]) return ''.join(result)

输入：s = "PAYPALISHIRING", numRows = 3 输出："PAHNAPLSIIGYIR"

排列过程：

1

P A H N A P L S I I G Y I R

算法步骤：

1.

创建 numRows 个空字符串

2.

遍历输入字符串的每个字符

3.

按 Z 字形顺序（先向下到底，再斜向上，再向下...）添加到对应行

4.

最后按行连接所有字符串

时间复杂度：O(n)，其中 n 是字符串长度 空间复杂度：O(n)

用户:

class ListNode:

class Solution:

1

def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]:

what the param list1 means

元宝:

list1 是一个指向链表头节点的指针（引用）。在 Python 中，虽然不像 C/C++ 那样有显式的指针，但这里 list1 实际上是一个指向 ListNode 对象的引用。

1234

class ListNode: def \_\_init\_\_(self, val=0, next=None): self.val = val # 当前节点的值 self.next = next # 指向下一个节点的引用

1234

\# 示例链表: 1 -> 2 -> 3 -> None list1 = ListNode(1) # 头节点 list1.next = ListNode(2) # 第二个节点 list1.next.next = ListNode(3) # 第三个节点

12345

def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: # list1: 第一个链表的头节点 # list2: 第二个链表的头节点 # 返回值: 合并后新链表的头节点 pass

123456789101112131415

\# 创建两个链表 # 链表1: 1 -> 3 -> 5 list1 = ListNode(1) list1.next = ListNode(3) list1.next.next = ListNode(5) # 链表2: 2 -> 4 -> 6 list2 = ListNode(2) list2.next = ListNode(4) list2.next.next = ListNode(6) # 调用函数合并 sol = Solution() merged = sol.mergeTwoLists(list1, list2) # 结果: 1 -> 2 -> 3 -> 4 -> 5 -> 6

1.

链表是节点通过 next 指针连接的结构

2.

list1 存储的是头节点的内存地址（引用）

3.

Optional\[ListNode\] 表示参数可以是：

ListNode 对象（有内容的链表）

None（空链表）

12345678

\# 空链表 empty\_list = None # 只有一个节点的链表 single\_node\_list = ListNode(1) # 1 -> None # 普通链表 normal\_list = ListNode(1, ListNode(2, ListNode(3))) # 1->2->3->None

1234567891011121314151617181920212223242526

def mergeTwoLists(self, list1, list2): # 1. 处理边界情况 if not list1: # 如果 list1 是 None（空链表） return list2 if not list2: # 如果 list2 是 None（空链表） return list1 # 2. 创建虚拟头节点简化操作 dummy = ListNode(0) current = dummy # 3. 遍历两个链表 while list1 and list2: if list1.val <= list2.val: current.next = list1 list1 = list1.next # 移动 list1 指针 else: current.next = list2 list2 = list2.next # 移动 list2 指针 current = current.next # 移动当前指针 # 4. 连接剩余部分 current.next = list1 if list1 else list2 return dummy.next # 返回真正的头节点

注意：list1 和 list2 是引用，不是整个链表的拷贝。在函数中修改 list1 = list1.next 只是移动了局部引用，不会影响原始链表。

用户:

what's the return type Optional\[ListNode\] means

元宝:

Optional\[ListNode\] 是 类型提示（Type Hinting），它表示函数返回值的类型可能是两种之一：

1

Optional\[ListNode\]

等价于：

1

Union\[ListNode, None\]

或：

1

ListNode | None

表示函数可能返回：

1.

一个 ListNode 对象（链表头节点）

2.

或者 None（空链表）

123456789101112131415

def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: # 如果两个链表都为空 if not list1 and not list2: return None # ✅ 符合 Optional\[ListNode\] 类型 # 如果 list1 为空 if not list1: return list2 # ✅ 返回 ListNode 或 None # 如果 list2 为空 if not list2: return list1 # ✅ 返回 ListNode 或 None # 正常情况 return new\_head # ✅ 返回 ListNode

1234567891011

def create\_linked\_list(values: List\[int\]) -> Optional\[ListNode\]: if not values: # 空列表 return None # ✅ 返回 None head = ListNode(values\[0\]) current = head for val in values\[1:\]: current.next = ListNode(val) current = current.next return head # ✅ 返回 ListNode

帮助 IDE 和类型检查器（如 mypy）理解代码：

12345678910

result = sol.mergeTwoLists(list1, list2) # 没有 Optional 类型提示时： result.next # IDE 不知道 result 可能为 None # 有 Optional 类型提示时： if result: # 明确检查是否为 None result.next # ✅ IDE 知道这里是安全的 else: print("结果是空链表")

明确告诉开发者这个函数可能返回空值：

123456789

\# 清晰表达了返回类型 def find\_node(head: ListNode, target: int) -> Optional\[ListNode\]: """查找值为 target 的节点，找不到则返回 None""" current = head while current: if current.val == target: return current current = current.next return None

12345678910111213141516171819202122

from typing import Optional class ListNode: def \_\_init\_\_(self, val=0, next=None): self.val = val self.next = next class Solution: def hasCycle(self, head: Optional\[ListNode\]) -> bool: # 处理空链表 if not head: return False # 正常逻辑... return True # 调用示例 sol = Solution() # 有效调用： print(sol.hasCycle(ListNode(1))) # 传入 ListNode print(sol.hasCycle(None)) # 传入 None

1234567891011

\# ❌ 不明确：调用者不知道可能返回 None def get\_middle(head: ListNode) -> ListNode: if not head: return None # 类型不一致！ #... # ✅ 明确：调用者知道要处理 None def get\_middle(head: Optional\[ListNode\]) -> Optional\[ListNode\]: if not head: return None #...

Python 3.10 支持更简洁的语法：

12345678

\# Python 3.10+ 推荐 def mergeTwoLists(self, list1: ListNode | None, list2: ListNode | None) -> ListNode | None: pass # 等价于 Python 3.9- from typing import Optional def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: pass

总结

Optional\[T\] 表示 "可能是 T 类型，也可能是 None"

在链表操作中很常见，因为空链表通常用 None 表示

提高代码的类型安全性和可读性

Python 3.10+ 推荐使用 T | None 语法

用户:

merge two ascending link list

class ListNode:

class Solution:

1

def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: if not list1 or not list2: return list1 if list1 else list2 # insert list1 into list2 cur2 = list2 cur1 = list1 # if list1 first element < list 2 first element # make list1 first element to be list 2 first element. if cur1.val < cur2.val: tmp1 = cur1.next tmp2 = cur2.next cur1.next = cur2 cur2 = cur1 cur1 = tmp1 list2 = cur2 while cur1 and cur2: if cur1.val >= cur2.val: tmp1 = cur1.next tmp2 = cur2.next cur2.next = cur1 cur1.next = tmp2 # cur point to cur1 element,cur1 point to list1's next node cur2 = cur1 cur1 = tmp1 else: cur2 = cur2.next if cur1: cur2.next = cur1 return list2

元宝:

你的代码逻辑基本正确，但有指针操作错误和边界处理不完善的问题。主要问题在于当 cur1.val >= cur2.val 时，你尝试将 cur1 插入到 cur2 之后，但 cur2.next 的连接逻辑有问题。

以下是修正后的版本：

123456789101112131415161718192021222324252627282930313233343536

\# Definition for singly-linked list. # class ListNode: # def \_\_init\_\_(self, val=0, next=None): # self.val = val # self.next = next class Solution: def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: # 处理空链表 if not list1 or not list2: return list1 if list1 else list2 # 确定头节点（较小值作为头） if list1.val < list2.val: head = list1 list1 = list1.next else: head = list2 list2 = list2.next cur = head # 当前合并位置 # 合并两个链表 while list1 and list2: if list1.val < list2.val: cur.next = list1 list1 = list1.next else: cur.next = list2 list2 = list2.next cur = cur.next # 连接剩余部分 cur.next = list1 if list1 else list2 return head

1\. 复杂且易错的指针操作

12345678

\# 你的代码： if cur1.val >= cur2.val: tmp1 = cur1.next tmp2 = cur2.next cur2.next = cur1 cur1.next = tmp2 # ❌ 问题在这里！ #...

问题：当 cur1 插入到 cur2 之后，cur1.next 应该指向 cur2.next 的原始值（即 tmp2），但此时 cur2.next 已经被修改了。

2\. 更简洁的虚拟头节点方法

12345678910111213141516171819

class Solution: def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: # 使用虚拟头节点简化操作 dummy = ListNode(0) # 虚拟头节点 cur = dummy while list1 and list2: if list1.val < list2.val: cur.next = list1 list1 = list1.next else: cur.next = list2 list2 = list2.next cur = cur.next # 连接剩余部分 cur.next = list1 if list1 else list2 return dummy.next # 返回真正的头节点

3\. 递归解法（简洁但可能栈溢出）

12345678910111213

class Solution: def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: if not list1: return list2 if not list2: return list1 if list1.val < list2.val: list1.next = self.mergeTwoLists(list1.next, list2) return list1 else: list2.next = self.mergeTwoLists(list1, list2.next) return list2

1234567891011121314151617181920212223242526272829303132333435363738394041424344454647

\# 测试函数 def test(): # 创建链表辅助函数 def create\_list(arr): if not arr: return None head = ListNode(arr\[0\]) cur = head for val in arr\[1:\]: cur.next = ListNode(val) cur = cur.next return head def to\_list(node): result = \[\] while node: result.append(node.val) node = node.next return result sol = Solution() # 测试用例 test\_cases = \[ (\[1,3,5\], \[2,4,6\]), # 正常情况 (\[\], \[1,2,3\]), # 一个为空 (\[1,2,3\], \[\]), # 另一个为空 (\[\], \[\]), # 都为空 (\[1\], \[2\]), # 单节点 (\[2\], \[1\]), # 单节点逆序 (\[1,5,7\], \[2,3,6,8\]) # 长度不同 \] for arr1, arr2 in test\_cases: list1 = create\_list(arr1) list2 = create\_list(arr2) merged = sol.mergeTwoLists(list1, list2) print(f"合并 {arr1} 和 {arr2}: {to\_list(merged)}") # 输出： # 合并 \[1, 3, 5\] 和 \[2, 4, 6\]: \[1, 2, 3, 4, 5, 6\] # 合并 \[\] 和 \[1, 2, 3\]: \[1, 2, 3\] # 合并 \[1, 2, 3\] 和 \[\]: \[1, 2, 3\] # 合并 \[\] 和 \[\]: \[\] # 合并 \[1\] 和 \[2\]: \[1, 2\] # 合并 \[2\] 和 \[1\]: \[1, 2\] # 合并 \[1, 5, 7\] 和 \[2, 3, 6, 8\]: \[1, 2, 3, 5, 6, 7, 8\]

123456789101112131415161718

class Solution: def mergeTwoLists(self, list1: Optional\[ListNode\], list2: Optional\[ListNode\]) -> Optional\[ListNode\]: dummy = ListNode(-1) # 虚拟头节点 cur = dummy while list1 and list2: if list1.val <= list2.val: cur.next = list1 list1 = list1.next else: cur.next = list2 list2 = list2.next cur = cur.next # 连接剩余的非空链表 cur.next = list1 or list2 return dummy.next

关键改进：

1.

使用虚拟头节点，避免特殊处理头节点

2.

更简洁的指针操作

3.

更好的可读性和维护性

（注：文档部分内容可能由 AI 生成）

TOC

0 comments
