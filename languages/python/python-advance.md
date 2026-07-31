# Python 3 进阶复习手册
> 数据结构 · 字符串处理 | Python 3.10+ | 13 个核心技巧

---

## 第一章：数据结构与算法相关问题与解决技巧

### 1.1 如何在列表、字典、集合中根据条件筛选数据

Python 提供三种核心筛选方式：**列表/字典/集合推导式**、内置函数 `filter()`，以及 `itertools.compress()`（配合掩码使用）。推导式是最 Pythonic 的方式，兼顾可读性与性能。

```python
# ── 列表筛选 ──────────────────────────────────────
data = [-3, 5, -1, 8, -2, 6, 0]

# 方式1: 列表推导式 (推荐)
pos = [x for x in data if x > 0]          # [5, 8, 6]

# 方式2: filter() —— 返回惰性迭代器，大数据更省内存
pos = list(filter(lambda x: x > 0, data))

# 方式3: itertools.compress (掩码筛选)
from itertools import compress
mask = [x > 0 for x in data]
pos = list(compress(data, mask))

# ── 字典筛选 ──────────────────────────────────────
prices = {'AAPL': 182, 'BABA': 78, 'TSLA': 245, 'NIO': 6}

# 字典推导式: 筛选价格 > 100 的股票
expensive = {k: v for k, v in prices.items() if v > 100}
# {'AAPL': 182, 'TSLA': 245}

# ── 集合筛选 ──────────────────────────────────────
nums = {1, 2, 3, 4, 5, 6}
evens = {x for x in nums if x % 2 == 0}   # {2, 4, 6}
```

> 💡 **性能建议**：数据量巨大时，优先用 `filter()` 或生成器表达式 `(x for x in data if ...)`，避免一次性构建完整列表占用内存。

---

### 1.2 如何为元组中的每个元素命名，提高程序可读性

原始元组用下标访问（`t[0]`、`t[2]`）可读性极差。有两种命名方案：`collections.namedtuple`（轻量，兼容元组所有操作）和 `typing.NamedTuple`（支持类型注解，更现代）。

```python
from collections import namedtuple
from typing import NamedTuple

# ── 方式1: namedtuple (经典) ───────────────────────
Student = namedtuple('Student', ['name', 'age', 'score'])
s = Student('Alice', 22, 95.5)

# 通过名称访问，清晰易读
print(s.name, s.score)          # Alice 95.5
# 仍然兼容元组下标和解包
name, age, score = s
print(s[0])                     # Alice

# _replace 返回新实例（namedtuple 不可变）
s2 = s._replace(score=98.0)

# ── 方式2: typing.NamedTuple (推荐，支持类型注解) ──
class Trade(NamedTuple):
    symbol: str
    price: float
    volume: int
    direction: str = 'BUY'  # 支持默认值

t = Trade('600519', 1680.0, 100)
print(t.symbol, t.direction)    # 600519 BUY
print(t._asdict())              # 转 dict
```

> 📝 **Note**：`NamedTuple` 是 `namedtuple` 的类语法糖，两者底层相同。如需可变字段，考虑 `dataclasses.dataclass`。

---

### 1.3 如何根据字典中值的大小，对字典中的项排序

字典本身无序排序概念（Python 3.7+ 插入有序）。对值排序的核心是 `sorted()` 配合 `key` 参数，常用 `operator.itemgetter` 或 `lambda`。

```python
from operator import itemgetter

scores = {'Alice': 88, 'Bob': 73, 'Charlie': 95, 'Diana': 81}

# ── 按值升序 ───────────────────────────────────────
asc = sorted(scores.items(), key=itemgetter(1))
# [('Bob', 73), ('Diana', 81), ('Alice', 88), ('Charlie', 95)]

# ── 按值降序 ───────────────────────────────────────
desc = sorted(scores.items(), key=itemgetter(1), reverse=True)

# ── lambda 等价写法 ────────────────────────────────
desc2 = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

# ── 只取 Top-N：用 heapq 更高效 ────────────────────
import heapq
top3 = heapq.nlargest(3, scores.items(), key=itemgetter(1))
# [('Charlie', 95), ('Alice', 88), ('Diana', 81)]

# ── 多字段排序：先按值降序，值相同则按键升序 ─────────
multi = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
```

> 💡 **性能对比**：`itemgetter` 是 C 实现，比等效的 `lambda` 快约 30%；`heapq.nlargest/nsmallest` 在 n 远小于数据量时，时间复杂度优于全量排序。

---

### 1.4 如何统计序列中元素的频度

`collections.Counter` 是专为频度统计设计的子类，支持加减运算、`most_common(n)` 等实用方法，是最优解。

```python
from collections import Counter

words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']

# ── 基本用法 ───────────────────────────────────────
c = Counter(words)
print(c)                # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(c['apple'])       # 3  (不存在的 key 返回 0 而非 KeyError)

# ── Top-N 最高频 ───────────────────────────────────
print(c.most_common(2)) # [('apple', 3), ('banana', 2)]

# ── 统计字符串字符频度 ─────────────────────────────
char_freq = Counter("programming")

# ── Counter 支持集合运算 ───────────────────────────
c1 = Counter('aababc')
c2 = Counter('abc')

combined = c1 + c2      # 合并计数
diff     = c1 - c2      # 差集计数 (只保留正数)
inter    = c1 & c2      # 取最小 (交集)
union    = c1 | c2      # 取最大 (并集)

# ── 统计词频 + 按频排名（工程常用）──────────────────
text = "the cat sat on the mat the cat"
word_freq = Counter(text.split())
for word, freq in word_freq.most_common():
    print(f"{word:10} {'█' * freq}")
```

**Counter 常用 API**：`most_common(n)` · `elements()` · `update(iterable)` · `subtract(iterable)` · `total()` *(3.10+)*

---

### 1.5 如何快速找到多个字典中的公共键 (key)

字典的 `.keys()` 返回**视图对象**，支持集合运算（交集 `&`、并集 `|`、差集 `-`）。利用这一特性，可以用一行代码完成多字典公共键查找。

```python
d1 = {'a': 1, 'b': 2, 'c': 3}
d2 = {'b': 4, 'c': 5, 'd': 6}
d3 = {'c': 7, 'd': 8, 'e': 9}

# ── 两个字典 ───────────────────────────────────────
common_2 = d1.keys() & d2.keys()   # {'b', 'c'}

# ── 多个字典: reduce + & ───────────────────────────
from functools import reduce

dicts = [d1, d2, d3]
common_all = reduce(lambda a, b: a & b, (d.keys() for d in dicts))
# {'c'}

# ── 等价写法: map + set.intersection ──────────────
common_all2 = set.intersection(*map(set, [d.keys() for d in dicts]))

# ── 找公共键并取各字典对应的值 ─────────────────────
for key in common_all:
    values = [d[key] for d in dicts if key in d]
    print(f"key={key}, values={values}")    # key=c, values=[3, 5, 7]
```

> 📝 **原理**：`dict.keys()` 返回 `dict_keys` 视图，实现了集合协议（`__and__`、`__or__` 等），无需转换 `set` 即可直接做集合运算，且是动态视图，字典变更后视图自动更新。

---

### 1.6 如何让字典保持有序

Python 3.7+ 中普通 `dict` 已按**插入顺序**有序。但若需要**访问顺序**排序（LRU 语义）或需要顺序敏感的相等比较，使用 `collections.OrderedDict`。

```python
from collections import OrderedDict

# ── Python 3.7+ dict 已按插入顺序有序 ────────────
d = {}
d['first']  = 1
d['second'] = 2
d['third']  = 3
list(d)  # ['first', 'second', 'third'] ✓

# ── OrderedDict 的独特能力: move_to_end ───────────
od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])

od.move_to_end('a')            # 'a' 移到末尾: b, c, a
od.move_to_end('c', last=False) # 'c' 移到首位: c, b, a
od.popitem(last=False)          # 弹出首项 (FIFO)
od.popitem(last=True)           # 弹出末项 (LIFO/Stack)

# ── OrderedDict 等值比较关注顺序 ──────────────────
od1 = OrderedDict([('a', 1), ('b', 2)])
od2 = OrderedDict([('b', 2), ('a', 1)])
od1 == od2   # False  (dict == dict 则 True)

# ── 实现 LRU Cache 概念 (手动版) ──────────────────
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache: return -1
        self.cache.move_to_end(key)  # 标记为最近使用
        return self.cache[key]

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 淘汰最旧
```

> ⚠️ **注意**：Python 3.7+ 的普通 `dict` 在大多数场景已足够，`OrderedDict` 的主要使用场景是：需要 `move_to_end`、顺序敏感的相等比较、或需要 `popitem(last=False)` 实现队列语义。

---

### 1.7 如何实现用户的历史记录功能（最多 n 条）

历史记录需要**固定长度的 FIFO 队列**——`collections.deque(maxlen=n)` 是最优数据结构，超出容量时自动淘汰最旧的记录，时间复杂度 O(1)。

```python
from collections import deque

# ── 基础用法 ───────────────────────────────────────
history = deque(maxlen=5)

for cmd in ['ls', 'cd /home', 'pwd', 'cat a.txt', 'vim b.py', 'git log']:
    history.appendleft(cmd)   # 新记录插入头部

print(list(history))
# ['git log', 'vim b.py', 'cat a.txt', 'pwd', 'cd /home']  (ls 已被淘汰)

# ── 封装为历史记录类 ───────────────────────────────
class SearchHistory:
    def __init__(self, max_size: int = 10):
        self._history: deque = deque(maxlen=max_size)

    def add(self, query: str) -> None:
        # 去重：如果已存在则移到最前
        if query in self._history:
            self._history.remove(query)
        self._history.appendleft(query)

    def clear(self) -> None:
        self._history.clear()

    def __iter__(self):
        return iter(self._history)

    def __len__(self):
        return len(self._history)

# 使用
sh = SearchHistory(max_size=3)
sh.add("RAG pipeline")
sh.add("LangChain")
sh.add("vector db")
sh.add("RAG pipeline")  # 重复，移到最前
print(list(sh))
# ['RAG pipeline', 'vector db', 'LangChain']
```

> 💡 **deque vs list**：`list` 头部插入/删除是 O(n)；`deque` 两端操作均为 O(1)，`maxlen` 参数让容量管理变成零代码。

---

## 第二章：复杂场景下字符串处理相关问题与解决技巧

### 2.1 如何拆分含有多种分隔符的字符串

`str.split()` 只支持单一分隔符。处理多种分隔符（如 CSV 变体、日志、自由文本）应使用 `re.split()`，支持正则表达式模式，灵活且高效。

```python
import re

s = "one,two;three|four  five\tsix"

# 以逗号、分号、竖线、空白字符为分隔符
result = re.split(r'[,;|\s]+', s)
# ['one', 'two', 'three', 'four', 'five', 'six']

# ── 保留分隔符（用捕获组）────────────────────────
result2 = re.split(r'([,;|])', "a,b;c")
# ['a', ',', 'b', ';', 'c']

# ── 预编译正则: 同一模式多次使用时提升性能 ─────────
SEPARATOR = re.compile(r'[,;|\s]+')
lines = ["a,b,c", "d;e;f", "g|h|i"]
parsed = [SEPARATOR.split(line) for line in lines]

# ── 过滤空字符串 (首尾分隔符可能产生空串) ──────────
raw = ",a,,b,c,"
clean = [x for x in re.split(r',', raw) if x]
# ['a', 'b', 'c']
```

---

### 2.2 如何判断字符串 a 是否以字符串 b 开头或结尾

使用 `str.startswith()` 和 `str.endswith()`，这两个方法都支持传入**元组**来同时匹配多个前/后缀，比正则表达式更快、更易读。

```python
filename = "report_2024.xlsx"
url      = "https://api.example.com/v1"

# ── 基本用法 ───────────────────────────────────────
filename.endswith('.xlsx')         # True
url.startswith('https')            # True

# ── 传入元组: 匹配多个后缀 ────────────────────────
EXCEL_EXTS = ('.xlsx', '.xls', '.csv')
filename.endswith(EXCEL_EXTS)      # True

# ── 过滤文件列表 ───────────────────────────────────
files = ['a.py', 'b.java', 'c.py', 'd.txt', 'e.pyx']
py_files = [f for f in files if f.endswith(('.py', '.pyx'))]
# ['a.py', 'c.py', 'e.pyx']

# ── 指定搜索范围: start/end 参数 ─────────────────
s = "Hello, World!"
s.startswith('World', 7)           # True (从下标7开始检查)

# ── 与 pathlib 配合 (推荐处理路径) ────────────────
from pathlib import Path
p = Path("data/report.xlsx")
p.suffix == '.xlsx'                # True (更语义化)
p.suffix in EXCEL_EXTS             # True
```

> 💡 **性能**：`startswith/endswith` 是 C 实现，比 `re.match` 快数倍。仅在需要复杂模式时才用正则。

---

### 2.3 如何调整字符串中文本的格式

常见需求包括：驼峰转下划线、日期格式转换、标准化大小写等。核心工具是 `re.sub()` 配合替换函数，以及字符串内置方法。

```python
import re

# ── 大小写转换 ─────────────────────────────────────
s = "hello world python"
s.upper()           # 'HELLO WORLD PYTHON'
s.title()           # 'Hello World Python'
s.capitalize()      # 'Hello world python'
s.swapcase()        # 'HELLO WORLD PYTHON'

# ── 驼峰命名 → 下划线命名 (CamelCase → snake_case) ─
def camel_to_snake(name: str) -> str:
    # 在大写字母前插入下划线
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

camel_to_snake('getUserName')   # 'get_user_name'
camel_to_snake('HTTPSRequest')  # 'https_request'

# ── 日期格式转换: MM/DD/YYYY → YYYY-MM-DD ─────────
date_str = "03/28/2026"
# 方式1: re.sub 捕获组
new_date = re.sub(r'(\d{2})/(\d{2})/(\d{4})', r'\3-\1-\2', date_str)
# '2026-03-28'
# 方式2: datetime (更鲁棒)
from datetime import datetime
dt = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")

# ── re.sub 传入函数替换 ────────────────────────────
# 将字符串中所有数字乘以2
result = re.sub(r'\d+', lambda m: str(int(m.group()) * 2), "foo12 bar5")
# 'foo24 bar10'

# ── 标准化空白 ────────────────────────────────────
messy = "  hello   world  \t python  \n"
clean = ' '.join(messy.split())   # 'hello world python'
```

---

### 2.4 如何将多个小字符串拼接成一个大的字符串

这是 Python 新手最容易踩坑的性能陷阱。`+` 拼接在循环中会产生大量中间对象（O(n²)）。正确方式是 `''.join(iterable)`，一次性分配内存，时间复杂度 O(n)。

```python
parts = ['Hello', 'Python', 'World']

# ── str.join ───────────────────────────────────────
result = ' '.join(parts)          # 'Hello Python World'
csv    = ','.join(parts)          # 'Hello,Python,World'
lines  = '\n'.join(parts)         # 多行

# ── join 接受任意可迭代对象 ────────────────────────
nums   = '-'.join(str(i) for i in range(5))   # '0-1-2-3-4'

# ── f-string: 少量拼接的可读首选 ─────────────────
name, score = 'Alice', 95
msg = f"Student {name} scored {score} points"

# ── io.StringIO: 复杂场景下的流式拼接 ────────────
import io
buf = io.StringIO()
for i in range(1000):
    buf.write(f"line {i}\n")
output = buf.getvalue()

# 性能排名 (短字符串): f-string ≈ join > % > format
# 性能排名 (大量拼接): join > StringIO >> +=
```

| 方式 | 场景 | 推荐度 |
|------|------|--------|
| `'sep'.join(lst)` | 列表/可迭代对象拼接 | ★★★★★ |
| `f"..."` | 少量变量插入，可读性优先 | ★★★★★ |
| `io.StringIO` | 复杂条件逻辑的流式构建 | ★★★★ |
| `s += t`（循环内） | 避免使用 | ★ |

---

### 2.5 如何对字符串进行左、右、居中对齐

Python 提供了 `str.ljust()`、`str.rjust()`、`str.center()` 三个方法，以及更强大的格式化语法（f-string / `format()`），支持自定义填充字符。

```python
s = 'Python'
W = 20

# ── 基本对齐方法 ──────────────────────────────────
s.ljust(W)              # 'Python              ' (左对齐, 空格填充)
s.rjust(W)              # '              Python' (右对齐)
s.center(W)             # '       Python       ' (居中)

# ── 自定义填充字符 ────────────────────────────────
s.ljust(W, '-')         # 'Python--------------'
s.rjust(W, '0')         # '00000000000000Python'
s.center(W, '*')        # '*******Python*******'

# ── format() / f-string 对齐语法 ─────────────────
#    <  左对齐  |  >  右对齐  |  ^  居中
print(f"{s:<20}")          # 左对齐, 宽度20
print(f"{s:>20}")          # 右对齐
print(f"{s:^20}")          # 居中
print(f"{s:*^20}")         # 居中, '*' 填充
print(f"{3.14159:>10.2f}") # '      3.14' 右对齐数字

# ── 打印对齐表格 ─────────────────────────────────
headers = ['Symbol', 'Price', 'Change']
rows    = [('AAPL', 182.5, '+1.2%'), ('BABA', 78.3, '-0.5%')]

print(f"{headers[0]:<10}{headers[1]:>10}{headers[2]:>10}")
print('-' * 30)
for sym, price, chg in rows:
    print(f"{sym:<10}{price:>10.1f}{chg:>10}")
```

> 📝 **f-string 格式迷你语言**：语法 `{value:[[fill]align][sign][width][.precision][type]}`。对齐符：`<` 左、`>` 右、`^` 居中；数字专用 `=` 在符号后填充。

---

### 2.6 如何去掉字符串中不需要的字符

根据场景选择：首尾去除用 `strip/lstrip/rstrip`；内部替换/删除用 `str.replace()` 或 `str.translate()`；复杂模式匹配用 `re.sub()`。

```python
import re

# ── 首尾去除 ───────────────────────────────────────
s = "  \t Hello, World! \n  "
s.strip()              # 'Hello, World!'  (两端空白)
s.lstrip()             # 左侧空白
s.rstrip()             # 右侧空白

# 指定去除字符集 (顺序无关, 逐字符匹配)
'---Hello---'.strip('-')      # 'Hello'
'xxHello!xx'.strip('x!')      # 'Hello'

# ── str.replace: 删除/替换特定子串 ────────────────
'Hello, World!'.replace(',', '')   # 'Hello World!'
'aababc'.replace('a', '')          # 'bbc'

# ── str.translate: 批量字符映射/删除 (高性能) ─────
# 删除标点符号
import string
table = str.maketrans('', '', string.punctuation)
"Hello, World! It's great.".translate(table)
# 'Hello World Its great'

# 字符替换 + 删除组合
table2 = str.maketrans({
    'a': '@',    # 替换
    'e': '3',    # 替换
    's': None,   # 删除
})
'password'.translate(table2)  # 'p@word'  (s被删除, a→@)

# ── re.sub: 正则匹配删除 ───────────────────────────
# 删除 HTML 标签
html = '<h1>Title</h1> <p>Content</p>'
text = re.sub(r'<[^>]+>', '', html)   # 'Title Content'

# 删除非ASCII字符
mixed = "Hello\x00\x01World\xff"
clean = re.sub(r'[^\x20-\x7E]', '', mixed)  # 'HelloWorld'

# 压缩多个空白为单个空格
re.sub(r'\s+', ' ', "  foo  bar\tbaz  ").strip()
# 'foo bar baz'
```

| 方法 | 适用场景 | 时间复杂度 |
|------|----------|------------|
| `strip/lstrip/rstrip` | 首尾字符去除 | O(k)，k=去除字符数 |
| `str.replace(old, new)` | 固定子串替换/删除 | O(n) |
| `str.translate(table)` | 批量单字符映射/删除 | O(n)，**最快** |
| `re.sub(pattern, '', s)` | 复杂模式匹配删除 | O(n)，常量因子较大 |

> 💡 **选择策略**：批量删除/替换**单个字符**时，`translate()` 是最快选择，因为它在 C 层用查找表实现，一次遍历完成所有映射。多字符子串替换用 `replace()`，模式匹配用 `re.sub()`。

---

*Python 3 进阶复习手册 · 完*
