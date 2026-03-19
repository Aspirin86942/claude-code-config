![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000000_a6962e7392333d82e1baf34f219769af09e777198da8b08db9e6fc1c87703c1e.png)

## python 脚本使⽤指南

⾦⼭⽂档的表格产品中引⼊了执⾏ Python 脚本能⼒，以期为⽤⼾提供⼀种更加灵活、⾼效的 数据处理⽅式。

## ⼀.主要特点

## 1.脚本内嵌在⽂档中

与表格⽂档数据⽆缝结合，跟随⽂档⼀同分享协作

## 2. 云端⼯作

云端编码，云端执⾏，⽆需本地开发环境

## 3. 使⽤ python 脚本完成数据分析全链路

## 数据连接 a.

- ⽀持从⼯作表、数据表中获取数据写⼊到表格
- 将两张表以主键列联表，为数据分析提供基础
- 同时还可以利⽤开源库从第三⽅应⽤获取数据，⽐如利⽤python获取数据库数据

## 数据清洗 b.

- 在获取数据函数中⽀持过滤参数，可以实现数据清洗

## 数据可视化 c.

利⽤丰富的第三⽅库，轻松实现数据分析可视化

- ▪

- 数据操作与分析：

Pandas、NumPy

- ▪

- 数据可视化： pyecharts

- ▪

- ⾦融数据： akshare、tushare、baostock 等等

- 将结果导⼊到表格 d.
- python 脚本输出的结果可以写⼊到表格
- python 脚本输出的结果也可以导出为图⽚

## ⼆.开始使⽤

使⽤ Python 脚本编辑器前，请先在 上新建或打开⼀个已有的 或 或 ⽂件 ⾦⼭⽂档 智能表格 表格 多维表格

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000001_96c6db52d3324097af1da90261e7be113851c583783a5a5772fd16809813e1d9.png)

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000002_98cfea1212d8987e6019ff3b95a6a1260a91680b08e5d60047d62355026a28e7.png)

## 三.使⽤ Python 访问表格⾥的数据

- 📌 ⾦⼭⽂档的表格类产品中有 ⼯作表ET 和 数据表DB 的区别，不同的表格类型，读取/写⼊数据要使⽤的函 数是不同的，下⾯展开说⼀下〜

## 3.1 使⽤ python 访问⼯作表⾥的数据

- 1.xl() 函数
- 函数签名

```
Plain Text
```

```
def xl(range: str = "", headers: bool = False, sheet_name: str | list[str] = "", book_url: str = "", start_row: int | None = None, start_column: int | None = None, end_row: int | None = None, end_column: int | None = None, formula: bool = False) -> __pd.DataFrame | dict[str, __pd.DataFr ame]: ... 1 2 3 4 5 6 7 8 9
```

## ◦ 参数列表

| 参数           | 类型          | 默认值   | 说明                                                 |
|--------------|-------------|-------|----------------------------------------------------|
| range        | str         | 空字符串  | ⼯作表中的选区描述。 默认为⼯作表中已经使⽤的区域。                         |
| headers      | bool        | False | 是否将当前选区第⼀⾏处理为表头。                                   |
| sheet_name   | str or list | 空字符串  | 选区所在的⼯作表名称，可为多个。 默认为当前激活的⼯作表。 如果为 则返回全部⼯作表数据。 None |
| book_url     | str         | 空字符串  | 选区所在的表格⽂件地址。 必须为⾦⼭⽂档云⽂档地址。 默认当前表格。                 |
| start_row    | int         | None  | 选区左上单元格的⾏，从0开始                                     |
| start_column | int         | None  | 选区左上单元格的列，从0开始                                     |
| end_row      | int         | 空值    | 选区右下单元格的⾏，从0开始                                     |
| end_column   | int         | 空值    | 选区右下单元格的列，从0开始                                     |
| formula      | bool        | False | 是否返回单元格内的公式内容                                      |

## ◦ ⽰例

以下⽰例会使⽤到如下虚拟的 表格，并假设当前正在打开的是 进销存 ⼯作表 1

（激活状态）

表格中的数据均虚构，仅做⽰例使⽤

|    | A                    | B        | C          |
|----|----------------------|----------|------------|
|  1 | 产品名称                 | 售价       | 发货日期       |
|  2 | iPhone 12            | 7999.00  | 2022/1/2   |
|  3 | MacBook Pro          | 12999.00 | 2023/5/11  |
|  4 | iPad Air 4           | 5499.00  | 2021/12/25 |
|  5 | AirPods Pro          | 1999.00  | 2022/11/30 |
|  6 | Apple Watch Series 7 | 3199.00  | 2023/8/15  |
|  7 | HomePod mini         | 749.00   | 2021/10/1  |
|  8 | iMac M1              | 9999.00  | 2022/9/22  |
|  9 | Mac mini M1          | 4599.00  | 2022/7/14  |
| 10 | Magic Keyboard       | 869.00   | 2022/2/28  |
| 11 | Magic Mouse 2        | 539.00   | 2022/6/5   |

## a.获取当前⼯作表（⼯作表1）中的所有数据，⽆表头

```
# 相当于 df = pandas.DataFrame(columns=None, data={ 全部数据 }) df1 = xl() # 由于⽆表头，只能按照索引访问 df 中的数据 # 下边这条语句会输出 ' 产品名称 ' print(df1[0][0]) 1 2 3 4 5 6 Plain Text
```

## b.获取当前⼯作表（⼯作表1）中的所有数据，⽆表头

```
# 相当于 df = pandas.DataFrame(columns=[A1:C1], data=[A2:C5]) df2 = xl("A1:C5", headers=True) # 可以通过列名来索引 df 中的数据 df2_subset = df[[' 产品名称 ', ' 发货⽇期 ']] 1 2 3 4 5 Plain Text
```

## c.获取⼯作表2（当前激活为⼯作表1）中，A1:G10区域的数据，将第⼀⾏处理为表头

```
df = pandas.DataFrame(columns=[A1:G1], data=[A2:G10]) Plain Text
```

```
# 相当于 df3 = xl("A1:G10", headers=True, sheet_name=" ⼯作表 2") 1 2
```

## d.获取其它表格⽂档（https://kdocs.cn/l/foo）中，⼯作表3的前 10 ⾏数据，第⼀⾏作为 表头

```
df4 = xl( range="1:10", headers=True, sheet_name=" ⼯作表 3", book_url="https://kdocs.cn/l/foo", ) 1 2 3 4 5 6 Plain Text
```

- e.获取当前表格中，所有⼯作表数据。

```
# 此时将返回⼀个 dict[str, pandas.DataFrame] 类型的 ds # ds 的 key 为⼯作表名称 ds = xl( headers=True, sheet_name=None, ) df5 = ds[' ⼯作表 1'] 1 2 3 4 5 6 7 8 Plain Text
```

## f. 获取当前表格（⼯作表1）中所有售价及发货⽇期数据

```
df6 = xl( start_row=0, start_column=1, ) 1 2 3 4 Plain Text
```

## 2.write\_xl() 函数

通过 函数将数据回写到⼯作表。 write\_xl

- 函数签名

```
Plain Text
```

```
def write_xl(data: object, range: str = "", new_sheet: bool = False, sheet_name: str = "", overfill: bool = True, book_url: str = "", start_row: int | None = None, start_column: int | None = None, 1 2 3 4 5 6 7 8
```

```
write_df_index: bool = False) -> None: 9
```

## ◦ 参数列表

| 参数             | 类型     | 默认值   | 说明                                                                                               |
|----------------|--------|-------|--------------------------------------------------------------------------------------------------|
| data           | object | 必填    | 要回写到⼯作表⾥的数据。 ⽀持的数据类型包括： Python基本数据类型； 维度不超过2维的容器类型，如： 和 ； ； 不⽀持写⼊图⽚。 list tuple pandas.DataFrame |
| range          | str    | 空字符串  | ⼯作表中的选区描述。 可以为⼀个单元格。为要写⼊数据的选区的左上⻆。 当 时可以为空。默认为新⼯作表的 位置。 new_sheet=True A1                        |
| new_sheet      | bool   | False | 是否将数据写⼊到新建的⼯作表中。                                                                                 |
| sheet_name     | str    | 空字符串  | 写⼊数据的选区所在的⼯作表名称。 当 时为表格中已经存在的⼯作表名称。 当 时为新建的⼯作表的名称。 new_sheet=False new_sheet=True                |
| overfill       | bool   | True  | 当 不⾜以容纳 时，是否允许超出部分继续写⼊。 如果设置为 超出 的 部分会被丢弃。 range data False range data                           |
| book_url       | str    | 字符串   | 指定写⼊的表格⽂件地址。 必须为⾦⼭⽂档云⽂档地址。 默认当前表格。                                                               |
| start_row      | int    | 空值    | 选区左上单元格的⾏，从0开始                                                                                   |
| start_column   | int    | 空值    | 选区左上单元格的列，从0开始                                                                                   |
| write_df_index | bool   | False | 是否写⼊ ⾥的index列 pandas.DataFrame                                                                   |

- ⽰例
- 将字符串、数字回写到⼯作表 a.

```
# 原始⼯作表 # +-------+-----+ # | Name  | Age | # +-------+-----+ # |  foo  |  1  | # +-------+-----+ # |  bar  |  2  | # +-------+-----+ # |  baz  |  3  | # +-------+-----+ # 删除 "B3:B4" 区域内的数据 delete_xl(range="B3:B4") # 删除后的⼯作表 # +-------+-----+ # | Name  | Age | # +-------+-----+ # |  foo  |  1  | # +-------+-----+ # |  bar  |     | # +-------+-----+ # |  baz  |     | # +-------+-----+ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 Plain Text
```

## 将 回写到⼯作表。 b. pandas.DataFrame

将 DataFrame 回写到⼯作表时，是按照数据在 中的相对位置（⾏/列）进⾏写⼊的。如果设置了 超过选区 的部分会被丢弃 DataFrame overfill=False range

Plain Text

```
import pandas as pd # 构造⼀个有 columns 的 DataFrame df = pd.DataFrame({"Name": ["foo", "bar", "baz"], "Age": [1, 2, 3]}) # 将 df 写⼊到当前⼯作表的 A1 位置 # 由于 df 中包含 columns 定义 # 最终会写⼊到 A1:B4 选区 # 相当于第 1 ⾏是表头，其余 3 ⾏为数据 # +-------+-----+ # | Name  | Age | # +-------+-----+ # |  foo  |  1  | # +-------+-----+ # |  bar  |  2  | # +-------+-----+ # |  baz  |  3  | # +-------+-----+ write_xl(df, "A1") # 构造⼀个⽆ columns 的 DataFrame df2 = pd.DataFrame([["foo", 1], ["bar", 2], ["baz", 3]]) # 将 df2 写⼊到当前⼯作表的 A1 位置 # 由于 df2 中没有 columns （未显式定义，默认使⽤ pandas.RangeIndex ） # 最终会写⼊到 A1:B3 选区 # 相当于没有表头，只有 3 ⾏数据 # +-------+-----+ # |  foo  |  1  | # +-------+-----+ # |  bar  |  2  | # +-------+-----+ # |  baz  |  3  | # +-------+-----+ write_xl(df2, "A1") # 也可以单独回写某个 series ，⾏为与只有⼀个 ' 列 ' 的 DataFrame ⼀致 write_xl(df['name'], "A1:B1") 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38
```

## 将 、 和 回写到⼯作表。 c. list tuple set

将⼀维 、 和 回写到⼯作表。 list tuple set

```
# 构造⼀个有 10 个元素的 list l = [i for i in range(10)] # 将 l 回写到以 A1 开头的⼀⾏中 # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+ # |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  | # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+ write_xl(l, "A1") # 将 l 回写到当前⼯作表的 A1:C1 区域 # 即将 l 回写成⼯作表中的⼀⾏ # 但是此时 A1:C1 选区不⾜以容纳 10 个元素 # 且 overfill=False 截断 l 中的元素 # +-----+-----+-----+ # |  0  |  1  |  2  | # +-----+-----+-----+ write_xl(l, "A1:C1", overfill=False) # 将 l 回写到当前⼯作表的 A1 ： A10 区域 # 与之前的⽰例相同，即将 l 回写成⼯作表中的⼀列 # +-----+ # |  0  | # +-----+ # |  1  | # +-----+ # |  2  | # +-----+ # |  3  | # +-----+ # |  4  | # +-----+ # |  5  | # +-----+ # |  6  | # +-----+ # |  7  | # +-----+ # |  8  | # +-----+ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 Plain Text
```

```
# |  9  | # +-----+ write_xl(l, "A1:A10") # 将 l 回写到当前⼯作表的 A1:E2 区域 # 即将 l 回写成⼯作表中 2 ⾏ *5 列 # 此时要求 l 的⻓度必须不⼤于选区的⻓度 # 否则⽆法判断该如何写⼊数据，导致报错 # +-----+-----+-----+-----+-----+ # |  0  |  1  |  2  |  3  |  4  | # +-----+-----+-----+-----+-----+ # |  5  |  6  |  7  |  8  |  9  | # +-----+-----+-----+-----+-----+ write_xl(l, "A1:E2") 40 41 42 43 44 45 46 47 48 49 50 51 52 53
```

将⼆维 、 和 回写到⼯作表。 list tuple set

```
# 构造⼀个⼆维的 list data = [["foo", 1], ["bar", 2], ["baz", 3]] # 将 data 回写到当前⼯作表的 A1 位置 # 将会在⼯作表中写⼊如下数据： # data 中的每⼀个⼦列表，被处理成⼯作表中的⼀⾏ # +-------+-----+ # |  foo  |  1  | # +-------+-----+ # |  bar  |  2  | # +-------+-----+ # |  baz  |  3  | # +-------+-----+ write_xl(data, "A1") 1 2 3 4 5 6 7 8 9 10 11 12 13 14 Plain Text
```

## 3.delete\_xl() 函数

通过 函数对数据进⾏删除操作。 delete\_xl

- 函数签名

## Plain Text

def delete\_xl(range: str = "", 1

sheet\_name: str | list[str] = '',

book\_url: str | None = '',

entire\_row: bool = False,

entire\_column: bool = False,

xl\_shift\_to\_left: bool = False,

start\_row: int | None = None,

start\_column: int | None = None,

drop\_sheet: bool = False):

2

3

4

5

6

7

8

9

## ◦ 参数列表

| 参数                | 类型                 | 默认值   | 说明                                        |
|-------------------|--------------------|-------|-------------------------------------------|
| range             | str                | 空字符串  | ⼯作表中的选区描述。                                |
| sheet_name        | str&#124;list[str] | 空字符串  | 写⼊数据的选区所在的⼯作表名称。                          |
| book_url          | str                | 字符串   | 指定写⼊的表格⽂件地址。 必须为⾦⼭⽂档云⽂档地址。 默认当前表格。        |
| entire_row        | bool               | False | 是否删除整⾏                                    |
| entire_colu mn    | bool               | False | 是否删除整列                                    |
| xl_shift_to_l eft | bool               | False | 是否向左合并，如果为 则向上合并 False                    |
| start_row         | int                | 空值    | ⼯作表中的起始⾏（从 开始） ，如果不传 则删除整⾏ 0 start_column |
| start_colum n     | int                | 空值    | ⼯作表中的起始列（从 开始） ，如果不传 则删除整列 0 start_row    |
| drop_sheet        | bool               | False | 是否删除整个⼯作表                                 |

- ⽰例

## 删除⼯作表某个范围的数据 a.

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000003_a23ca8723560ef6433b0ec4e73295698d1a802bee1b1d9db9c6eb2e9461c46c1.png)

## 删除某⾏或某列数据 b.

```
# 原始⼯作表 +-------+-----+ | Name  | Age | +-------+-----+ |  foo  |  1  | +-------+-----+ |  bar  |  2  | +-------+-----+ |  baz  |  3  | +-------+-----+ 删除 "B3:B4" 区域内的数据 delete_xl(range="B3:B4") 删除后的⼯作表 +-------+-----+ | Name  | Age | +-------+-----+ |  foo  |  1  | +-------+-----+ |  bar  |     | +-------+-----+ |  baz  |     | +-------+-----+ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 Plain Text
```

## 删除整个⼯作表 c.

```
1 delete_xl(sheet_name="sh1", drop_sheet=True) Plain Text
```

## 3.2 使⽤ python 访问数据表⾥的数据

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000004_9f4792d77e60781c0ccc6fa82da6c11e7c019aa71941b9c22c28c76419651e08.png)

由于数据表中的类型并不能简单使⽤ 来承载，因此对数据表读写的⽀持⽬前还不完 善。 pandas.DataFrame

## 1.数据表中的字段类型

不同于传统的表格产品，数据表中的每个字段，都是有类型的。这些类型包括：

| 字段类型           | 类型名称   | 值类型     | 说明            |
|----------------|--------|---------|---------------|
| MultiLineText  | ⽂本     | string  |               |
| Date           | ⽇期     | string  |               |
| Time           | 时间     | string  |               |
| Number         | 数值     | numeric |               |
| Currency       | 货币     | numeric |               |
| Percentage     | 百分⽐    | numeric |               |
| ID             | ⾝份证    | string  |               |
| Phone          | 电话     | string  |               |
| Email          | 电⼦邮箱   | string  |               |
| URL            | 超链接    | object  | 不⽀持通过Python更新 |
| Checkbox       | 复选框    | boolean |               |
| SingleSelect   | 单选项    | object  | 不⽀持通过Python更新 |
| MultipleSelect | 多选项    | object  | 不⽀持通过Python更新 |
| Rating         | 等级     | numeric | 会被降级成Number类型 |
| Complete       | 进度条    | numeric |               |
| Contact        | 联系⼈    | object  | 不⽀持通过Python更新 |
| Attachment     | 附件     | object  | 不⽀持通过Python更新 |
| Link           | 关联     | object  | 不⽀持通过Python更新 |
| Note           | 富⽂本    | object  | 不⽀持通过Python更新 |
| Address        | 地址     | object  | 不⽀持通过Python更新 |
| Cascade        | 级联     | object  | 不⽀持通过Python更新 |

## 以下类型为数据表中的⾃动类型，即该类型的记录值是系统⾃动填充的，不⽀持外部更新。

| 字段类型             | 类型名称   |
|------------------|--------|
| AutoNumber       | 编号     |
| CreatedBy        | 创建者    |
| CreatedTime      | 创建时间   |
| LastModifiedBy   | 最后修改者  |
| LastModifiedTime | 最后修改时间 |
| Formula          | 公式     |
| Lookup           | 引⽤     |

## 2.dbt() 函数

使⽤ 函数读取数据表中的数据。 dbt()

## ◦ 函数签名

```
def dbt(field: str | list[str] = None, sheet_name: str | list[str] = '', book_url: str = '') -> __pd.DataFrame | dict[str, __pd.DataFram e, condition: dict = {}]: 1 2 3 4 Plain Text
```

## ◦ 参数列表

| 参数          | 类型          | 默认值   | 说明                                                 |
|-------------|-------------|-------|----------------------------------------------------|
| field       | str or list | None  | 要返回的字段列表。 默认为 ，表⽰返回所有字段。 None                      |
| sheet_na me | str or list | 空字符串  | 字段所在的数据表名称，可为多个。 默认为当前激活的数据表。 如果为 则返回全部数据表数据。 None |
| book_url    | str         | 空字符串  | 字段所在的表格⽂件地址。 必须为⾦⼭⽂档云⽂档地址。 默认当前表格。                 |
| condition   | dict        | {}    | 过滤条件，细节参考附件1：dbt函数筛选记录说明                           |

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000005_4cd5555b6d1953d554f748d0372c95215b04dca2b173860f8e606f1d76111b20.png)

## ◦ ⽰例

以下⽰例会使⽤到如下虚拟的 表格，并假设当前正在打开的是 读取当前数据表 中的产品名称和库存数量 进销存 数据表 1 数据表 1

表格中的数据均虚构，仅做⽰例使⽤

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000006_ab3504ec86c06ce79a23464821043133fb03a863d5bc9f8905fa3242db7d98f9.png)

| 口   | P产品名称                | 123库存数量   | 进货日期       | ?进货价格      |   + |
|-----|----------------------|-----------|------------|------------|-----|
| 1   | iPhone 12            | 100.00    | 2022/01/02 | ￥7,999.00  | 449 |
| 2   | MacBook Pro          | 175.00    | 2023/05/11 | ￥12,999.00 | 449 |
| 3   | iPad Air 4           | 173.00    | 2021/12/25 | ￥5,499.00  | 449 |
| 4   | AirPods Pro          | 238.00    | 2022/11/30 | ￥1,999.00  | 449 |
| 5   | Apple Watch Series 7 | 1024.00   | 2023/08/15 | ￥3,199.00  | 449 |
| 6   | HomePod mini         | 364.00    | 2021/10/01 | ￥749.00    | 449 |
| 7   | iMac M1              | 874.00    | 2022/09/22 | ￥9,999.00  | 449 |
| 8   | Mac mini M1          | 85.00     | 2022/07/14 | ￥4,599.00  | 449 |
| 9   | Magic Keyboard       | 56.00     | 2022/02/28 | ￥869.00    | 449 |
| : ← | Magic Mouse 2        | 1.00      | 2022/06/05 | ￥539.00    | 449 |
| +   |                      |           |            |            | 449 |

- 读取当前数据表（数据表1）中的产品名称和库存数量。 a.
- 读取当前数据表中，数据表1和数据表2的所有记录 b.
- 读取其它⽂档( ) 中的全部数据表中记录 c. https://www.kdocs.cn/l/bar

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000007_7a189433080486ea23591be93714869a1fd551b22ed06561959eabaf79fcf221.png)

```
# 此时返回的是⼀个包括两个 DataFrame 的 dict ds = dbt(sheet_name=[' 数据表 1', ' 数据表 2']) df1 = ds[' 数据表 1'] df2 = ds[' 数据表 2'] 1 2 3 4 Plain Text
```

```
# 此时返回的是⼀个包括多个 DataFrame 的 dict ds = dbt(sheet_name=None, book_url="https://www.kdocs.cn/l/bar") 1 2 Plain Text
```

## 3.insert\_dbt() 函数

使⽤ 函数向数据表中写⼊新记录。 insert\_dbt()

## ◦ 函数签名

```
def insert_dbt(data: dict[str, any] | list[dict[str, any]] | __pd.DataF rame, sheet_name: str = '', new_sheet: bool = False) -> None: 1 2 3 Plain Text
```

## ◦ 参数列表

| 参数         | 类型     | 默认值   | 说明                                                                                                         |
|------------|--------|-------|------------------------------------------------------------------------------------------------------------|
| data       | object | 必填    | 要回写到数据表⾥的数据。 ⽀持的数据类型包括： 包含记录名称和值的 ； 维度不超过2维的 类型； ； 不⽀持写⼊附件等复杂类型。 dict[str, any] dict list pandas.DataFrame |
| sheet_name | str    | 空字符串  | 写⼊数据的选区所在的数据表名称。 当 时为表格中已经存在的数据表名称。 当 时为新建的数据表的名称。 new_sheet=False new_sheet=True                          |
| new_sheet  | bool   | False | 是否将数据写⼊到新建的数据表中。                                                                                           |

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000008_51948451cf53770ac6c6da75fca93166b2a299d895d649bd426cecc9108cb596.png)

提⽰

建议直接使⽤ 函数返回的 ，进⾏所需要的处理后，回写数据表。 dbt() DataFrame

- ⽰例

```
# 返回数据表 1 中的字段名为产品名称和库存数量的记录，表头为字段名 # 返回的数据类似下表所⽰ # 其中 B ， C ， D 为 Index 中保存的记录 ID # +-----+-------------+----------+ # |     | 产品名称 | 库存数量 | # +-----+-------------+----------+ # |  B  |  iPhone 12  |   100    | # +-----+-------------+----------+ # |  C  | MacBook Pro |   175    | # +-----+-------------+----------+ # |  D  | iPad Air 4  |   173    | # +-----+-------------+----------+ df = dbt(field=[' 产品名称 ', ' 库存数量 ']) # 将 df 中的数据写⼊到新的数据表 2 中 insert_dbt(df, sheet_name=" 数据表 2", new_sheet=True) # 向数据表 2 中，新增⼀条记录 insert_dbt({" 产品名称 ": "iPad Air 5", " 库存数量 ": 100 }, sheet_name=" 数据表 2") # 向数据表 2 中，新增两条记录 insert_dbt([{" 产品名称 ": "Mac mini M2"}, {" 产品名称 ": "Mac mini M2 Pro"}] , sheet_name=" 数据表 2") 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22
```

## 4.update\_dbt() 函数

使⽤ 函数更新数据表中记录 update\_dbt()

## ◦ 函数签名

```
def update_dbt(data: dict[str, any] | list[dict[str, any]] | __pd.DataF rame, sheet_name: str = '') -> None: 1 2 Plain Text
```

## ◦ 参数列表

| 参数         | 类型     | 默认值   | 说明                                                                                                            |
|------------|--------|-------|---------------------------------------------------------------------------------------------------------------|
| data       | object | 必填    | 要回写到数据表⾥的数据。 ⽀持的数据类型包括： 包含记录ID、名称和值的 ； 维度不超过2维的 类型； ； 不⽀持写⼊附件等复杂类型。 dict[str, any] dict list pandas.DataFrame |
| sheet_name | str    | 空字符串  | 写⼊数据的选区所在的数据表名称。 当 时为表格中已经存在的数据表名称。 当 时为新建的数据表的名称。 new_sheet=False new_sheet=True                             |

## ◦ ⽰例

```
Plain Text
```

```
# 返回数据表 1 中的字段名为产品名称和库存数量的记录，表头为字段名 # 返回的数据类似下表所⽰ # 其中 B ， C ， D 为 Index 中保存的记录 ID # +-----+-------------+----------+ # |     | 产品名称 | 库存数量 | # +-----+-------------+----------+ # |  B  |  iPhone 12  |   100    | # +-----+-------------+----------+ # |  C  | MacBook Pro |   175    | # +-----+-------------+----------+ # |  D  | iPad Air 4  |   173    | # +-----+-------------+----------+ df = dbt(field=[' 产品名称 ', ' 库存数量 ']) # 修改 df 中的数据，并更新数据表中的记录 df[' 库存数量 '] = df[' 库存数量 '] * 2 update_dbt(df) # 单独修改数据表 1 中的记录 # 其中包括 ID 字段 _rid 值为对应的 Index 中的值 update_dbt({"_rid": "B", " 产品名称 ": "iPhone 12 Pro"}) # 更新多条记录的值 update_dbt([{"_rid": "C", " 产品名称 ": "MacBook Pro M1"}, {"_rid": "D", " 库存数量 ": 200}]) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
```

## 5.delete\_dbt() 函数

使⽤ 函数删除数据表中的数据。 delete\_dbt()

- 函数签名

```
def dbt(sheet_name: str | list[str] = '', book_url: str = '') -> __pd.DataFrame | dict[str, __pd.DataFram e, condition: dict = {}]: 1 2 3 Plain Text
```

## ◦ 参数列表

| 参数         | 类型          | 默认值   | 说明                                                 |
|------------|-------------|-------|----------------------------------------------------|
| sheet_name | str or list | 空字符串  | 字段所在的数据表名称，可为多个。 默认为当前激活的数据表。 如果为 则返回全部数据表数据。 None |
| book_url   | str         | 空字符串  | 字段所在的表格⽂件地址。 必须为⾦⼭⽂档云⽂档地址。 默认当前表格。                 |
| condition  | dict        | {}    | 过滤条件，细节参考附件1：dbt函数筛选记录说明 当没有                       |

## ◦ ⽰例代码

## 以下⽰例会使⽤到如下虚拟的 ⼩费的信息

![Image](D:\Program_python\docling\output\md\python脚本使用指南_artifacts\image_000009_531f4123bb562c13e529fa8cffc044aa6eea7ab42c0f080e06c613821be950c3.png)

## case1: 删除整表数据 a.

```
delete_dbt(sheet_name=[" 数据表 "]) 1 Python
```

## case2:  根据条件删除数据。 如下代码，删除 ⻝物为'炸蘑菇'的数据 b.

```
delete_dbt( sheet_name=[" ⼩费数据 "], condition={ "mode": "AND", "criteria": [ { "field": " ⻝物 ", "op": "Intersected", "values": [ " 炸蘑菇 " ] } ] }) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 Python
```

## 四.内置的第三⽅库

## · pandas

Pandas 是⼀个开源的数据分析和数据处理库，它是基于NumPy构建的，提供了⾼性能、易于 使⽤的数据结构和数据分析⼯具，使得在Python中进⾏数据处理和分析变得更加简单和⾼效

- requests

requests 库是 Python 的⼀个 HTTP 客⼾端库，可以帮助⽤⼾发送各种类型的HTTP请求，如 GET、POST、PUT、DELETE 等，并获取响应。requests 库具有简单易⽤、功能强⼤、灵活性 ⾼等特点，因此被⼴泛应⽤于Python⽹络编程中

## · akshare

AkShare 是基于 Python 的开源⾦融数据接⼝库，⽬的是实现对股票、期货、期权、基⾦、债 券、外汇等⾦融产品和另类数据从数据采集，数据清洗到数据下载的⼯具，满⾜⾦融数据科学

## · astropy

Astropy ⽤于天⽂学数据处理和分析。它提供了许多有⽤的⼯具和函数来操作各种类型的天⽂ 学数据，从图像和表格到天体物理学常⻅的坐标系转换和单位转换

## · baostock

BaoStock 是⼀个证券数据服务平台。考虑到 Python pandas 包在⾦融量化分析中体现出的优 势， BaoStock 返回的绝⼤部分的数据格式都是 pandas DataFrame 类型，⾮常便于⽤ pandas/NumPy/Matplotlib 进⾏数据分析和可视化

## · bs4

Beautiful Soup（简称 BS4）是⼀个⽤于解析 HTML 和 XML ⽂档的 Python 库。它提供了⼀种 简单⽽灵活的⽅式来导航、搜索和修改解析树，使得从⽹⻚中提取数据变得更加容易

## · Cartopy

Cartopy 是⼀个 Python 包，⽤于地理空间数据处理，以便⽣成地图和其他地理空间数据分 析。 Cartopy 利⽤了强⼤的PROJ.4、NumPy 和 Shapely 库，并在 Matplotlib 之上构建了⼀个 编程接⼝，⽤于创建发布⾼质量的地图

## · imbalanced-learn

imbalanced-learn 提供了⼀些技术来解决数据不平衡的问题。在分类问题中，如果数据集中的 ⼀个类别的样本数量远远⼤于另⼀个类别，这会导致模型对多数类别的偏向，从⽽降低对少数 类别的识别能⼒。这种情况下，imbalanced-learn库可以帮助提⾼模型对少数类别的识别能⼒

## · IPython

IPython 是⼀个交互式计算环境的扩展库，提供了⼀个强⼤的交互式环境和⼯具集，提供了许 多⽅便的功能和特性，使得开发者可以更加⾼效地编写、测试和调试Python代码。它是

Python 数据科学和机器学习领域中常⽤的⼯具之⼀

## · matplotlib

Matplotlib 是 Python 中⼀个常⽤的绘图库，可以⽤于绘制各种类型的图表，包括线图、散点 图、条形图、等⾼线图、3D图等等。它是⼀个⾮常强⼤和灵活的库，被⼴泛⽤于数据科学、机 器学习、⼯程学、⾦融等领域

## · networkx

NetworkX 是⼀个⽤于创建、操作和学习复杂⽹络的Python库。它提供了⼀组丰富的⼯具和算 法，⽤于分析和可视化⽹络结构，以及研究⽹络的属性和⾏为

## · nltk

Natural Language Toolkit（简称 NLTK）是⼀个⽤于⾃然语⾔处理（NLP）的 Python 库。它 提供了⼀系列⼯具和数据集，⽤于处理、分析和理解⽂本数据

## · numpy

NumPy（Numerical Python）是⼀个⽤于科学计算的Python 库。它提供了⼀个⾼性能的多维 数组对象（ndarray）和⼀组⽤于操作数组的函数，使得在Python中进⾏数值计算和数据处理 变得更加⾼效和⽅便

## · pyecharts

Pyecharts 是⼀个⽤于⽣成交互式图表和可视化的Python库，它基于Echarts JavaScript 库， 并提供了⼀种简单⽽强⼤的⽅式来创建各种类型的图表。通过Pyecharts，可以轻松地将数据 转化为各种图表，如折线图、柱状图、散点图、饼图等等，并且可以对图表进⾏各种定制，如 修改颜⾊、添加标签、调整字体等等。使⽤Pyecharts可以⼤⼤提⾼数据可视化的效率，让⽤ ⼾更加直观地了解数据的分布和规律。同时，Pyecharts也⽀持多种输出格式，如HTML、 PDF 等，⽅便⽤⼾将图表嵌⼊到Web⻚⾯或⽣成报告中使⽤

## · pymysql

PyMySQL 是 Python 中⽤于连接和操作 MySQL 数据库的⼀个库。它提供了Python编程语⾔ 和MySQL数据库之间的接⼝，使得Python程序可以⽅便地连接、查询和操作MySQL数据库

## · pywavelets

PyWavelets 是 Python 中⽤于⼩波变换的免费开源库。⼩波是在时间和频率上都局部化的数学 基函数，⼩波变换则是利⽤⼩波的时频变换来分析和处理信号或数据。PyWavelets提供了丰富

的功能和灵活的接⼝，可以对图像、⾳频、信号等数据进⾏⼩波变换、逆变换、阈值去噪、压 缩等操作。此外，PyWavelets还⽀持多种⼩波基函数和边界处理⽅式，⽤⼾可以根据需要选择 合适的⼩波基函数和参数

## · scikit-image

Scikit-image 是⼀个基于 Python 脚本语⾔开发的数字图⽚处理包，它将图⽚作为numpy数组 进⾏处理，正好与matlab⼀样。scikit-image 对 scipy.ndimage 进⾏了扩展，提供了更多的图 ⽚处理功能。Scikit-image 库包含了⼀些基本的图像处理功能，⽐如图像缩放、旋转、图像变 换、阈值化处理等等。此外，它还包含了众多⾼级图像处理算法，⽐如边缘检测、形态学操 作、直线和圆检测等等

## · scikit-learn

Scikit-learn （以前称为 scikits.learn，也称为 sklearn）是⼀个简单⾼效的数据挖掘和数据分 析⼯具，建⽴在Python编程语⾔之上。它是为了解决真实世界中的问题⽽开发的，并且在学 术和商业环境中都得到了⼴泛的应⽤。Scikit-learn的主要功能包括分类、回归、聚类、降维、 模型选择和预处理

## · scipy

scipy 是⼀个基于 Python 的开源科学计算库，它建⽴在NumPy库的基础上，提供了更⾼级的 数学、科学和⼯程计算功能。scipy库包含了许多模块，每个模块都提供了⼀组相关的函数和⼯ 具，⽤于解决各种数学、科学和⼯程问题

## · seaborn

Seaborn 是⼀个基于 Python 的数据可视化库，它在matplotlib 的基础上进⾏了更⾼级的API 封装，使得作图更加容易，并且制作出来的图形也更加美观和具有吸引⼒。Seaborn提供了⼀ 种⾼度交互式界⾯，便于⽤⼾能够做出各种有吸引⼒的统计图表

## · statsmodels

statsmodels 是⼀个 Python 库，提供了⽤于统计建模和计量经济学的函数和类。它包含了⼀系 列统计模型，⽤于数据分析、探索性数据分析(EDA)、建模和推断。该库的⽬标是提供⼀种简单 ⽽⼀致的接⼝，使得⽤⼾可以在Python中进⾏各种统计任务

## · sympy

sympy 是⼀个基于Python 的符号计算库，它提供了符号计算的功能，可以进⾏符号代数、微 积分、线性代数、离散数学等⽅⾯的计算。与其他数值计算库不同，sympy库执⾏的是精确计

## 算，⽽不是数值近似，这使得它⾮常适合⽤于数学推导、符号计算和数学建模

## · tushare

tushare 是⼀个基于 Python 的⾦融数据接⼝库，它提供了丰富的⾦融市场数据，包括股票、指 数、基⾦、期货、外汇等数据。tushare库获取数据的来源是中国的⾦融市场，可以帮助获取 和分析⾦融数据

## · qrcode

qrcode 是⼀个基于 Python 的⼆维码⽣成库，它可以将⽂本、URL或其他数据转换成⼆维码图 像。该库⽀持⾃定义⼆维码的⼤⼩、颜⾊、纠错级别等参数，同时还可以在⼆维码中添加logo 图⽚。它的API简单易⽤，既可以⽣成基本的⿊⽩⼆维码，也可以创建带有⾃定义样式的艺术 ⼆维码。

```
import qrcode # ⽣成⼆维码 qr = qrcode.QRCode( version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4, ) qr.add_data('https://www.baidu.com') qr.make(fit=True) img = qr.make_image(fill_color="black", back_color="white") img.show() 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 Python
```

## · jionlp

jionlp 是⼀个中⽂ NLP ⼯具包，提供了⼤量常⽤的中⽂⽂本处理功能，包括⽂本清洗、实体识 别、地址解析、时间解析、摘要⽣成、新闻分类等。它设计简洁，即装即⽤，能够帮助开发者 快速处理中⽂⽂本数据，适⽤于各类中⽂NLP任务。

```
import jionlp as jio text = ' 有疑问请联系张⼩姐 18340234920 ，或拨打 (028)58291283 。 ' phones = jio.remove_phone_number(text) 1 2 3 4 Python
```

## · jieba

jieba 是最常⽤的中⽂分词库之⼀，它提供了多种分词模式，包括精确模式、全模式、搜索引擎 模式等。除了基本分词功能外，jieba还⽀持⾃定义词典、关键词提取、词性标注等功能。它采 ⽤基于前缀词典实现⾼效的词图扫描，使⽤动态规划查找最⼤概率路径，具有较好的分词准确 率。

```
import jieba seg_list = jieba.cut(" 我来到北京清华⼤学 ", cut_all=True) print("Full Mode: " + "/ ".join(seg_list))  # 全模式 seg_list = jieba.cut(" 我来到北京清华⼤学 ", cut_all=False) print("Default Mode: " + "/ ".join(seg_list))  # 精确模式 seg_list = jieba.cut(" 他来到了⽹易杭研⼤厦 ")  # 默认是精确模式 print(", ".join(seg_list)) seg_list = jieba.cut_for_search(" ⼩明硕⼠毕业于中国科学院计算所，后在⽇本京都⼤ 学深造 ")  # 搜索引擎模式 print(", ".join(seg_list)) 1 2 3 4 5 6 7 8 9 10 11 12 13 Python
```

## · faker

faker 是⼀个⽤于⽣成假数据的Python库，它可以⽣成各种类型的虚拟数据，包括姓名、地 址、电话号码、邮箱、公司名称、信⽤卡号等。⽀持多种语⾔和地区的数据格式，对于开发测 试、数据库填充、演⽰样例等场景⾮常有⽤。

```
from faker import Faker fake = Faker() print(f"Name: {fake.name()}") print(f"Address: {fake.address()}") print(f"Text: {fake.text()}") 1 2 3 4 5 6 7 Python
```

## · pypinyin

pypinyin 是⼀个汉字转拼⾳的Python 库，⽀持将中⽂汉字转换为拼⾳，提供多种拼⾳⻛格 （包括带声调、数字声调、⽆声调等） ，可以处理多⾳字，⽀持⾃定义词库。它常⽤于中⽂⽂本 的拼⾳化、汉字排序、模糊搜索等场景。

```
from pypinyin import pinyin print(pinyin(' 中⼼ ')) 1 2 3 Python
```

## · polars

polars 是⼀个⾼性能的数据处理库，使⽤Rust语⾔编写并提供Python接⼝。它提供了类似 pandas 的 DataFrame API，但在处理⼤规模数据时具有更好的性能。polars⽀持惰性计算、 并⾏处理、内存优化等特性，适合处理⼤规模数据分析和数据处理任务，特别是在需要⾼性能 计算的场景下。

```
import polars as pl # 创建⼀个简单的 DataFrame df = pl.DataFrame({ "A": [1, 2, 3, 4], "B": [5, 6, 7, 8] }) # 查看 DataFrame print(df) # 选择列 print(df.select(["A", "B"])) # 过滤⾏ print(df.filter(pl.col("A") > 2)) # 排序 print(df.sort(by="A")) # 聚合 print(df.group_by("A").agg(pl.col("B").mean())) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 Python
```

## 附件1：dbt 函数筛选记录说明

在 dbt 中，使⽤ condition 参数对数据进⾏筛选，说明如下、

## 1. condition 参数格式

```
{ "mode": "AND", // 选填。表⽰各筛选条件之间的逻辑关系。只能是 "AND" 或 "OR" 。缺 省值为 "AND" "criteria": [ // 结构体内必填。包含筛选条件的数组。每个字段上只能有⼀个筛选条 件 { "field": " 名称 ", // 必填。根据 preferId 与否，需要填⼊字段名或字段 id "op": "Intersected", // 必填。表⽰具体的筛选规则，⻅下 "values": [ // 必填。表⽰筛选规则中的值。数组形式。 " 多维表 ", // 值为字符串时表⽰⽂本匹配 "12345" ] }, { "field": " 数量 ", "op": "greager", "values": [ "1" ] } ] } 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
```

注 1：这⾥的 必须⼤写，否则会出错 mode

注 2：这⾥的 ，必须是⼀个数组，传 ，相当于传 values [" 多维表 "] [{ type:

，即不传默认帮你补充 类型 多维表 ' }] Text

注 3：复选框的值， 代表否， 代表是 values: ['0'] value: ['1']

'Text', value: '

## 2. 筛选条件 op 参数说明

## JSON

- "Equals": 1

等于

- "NotEqu": 2

不等于

- "Greater": 3

⼤于

- "GreaterEqu": 4

⼤等于

- "Less": 5

⼩于

- "LessEqu": 6

⼩等于

- "GreaterEquAndLessEqu": 7

介于（取等）

- "LessOrGreater": 8

介于（不取等）

- "BeginWith": 9

开头是

- "EndWith": 10

结尾是

- "Contains": 11

包含

- "NotContains": 12

不包含

- "Intersected": 13

指定值

- "Empty": 14

为空

- "NotEmpty": 15

不为空

values[] 数组内的元素为字符串时，表⽰⽂本匹配

各筛选规则独⽴地限制了values数组内最多允许填写的元素数，当values内元素数超过阈 值时，该筛选规则将失效。

- '为空、不为空'不允许填写元素； a.

- '介于'允许最多填写2个元素； b.

- '指定值'允许填写65535个元素； c.

- 其他规则允许最多填写1个元素 d.

使⽤指定值（Intersected）操作符时，values 中填写的值，应该是多维表中实际展⽰的值。⽐ 如筛选'货币'类型的列时，应带上货币符号，⽐如：

```
{ "mode": "AND", "criteria": [{ "field": " 货币列 ", "op": "Intersected", "values": [ "$16.99" ] }] } 1 2 3 4 5 6 7 8 9 10 SQL
```

## 3. ⽇期的动态筛选

⽬前还⽀持对⽇期进⾏动态筛选，此时values[]内的元素需以结构体的形式给出：

```
condition = { "mode": "AND", "criteria": [ { "field": " ⽇期 ", "op": "Equals", "values": [ { "dynamicType": "lastMonth", "type": "DynamicSimple" } ] } ] } 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 JSON
```

上述⽰例对应的筛选条件为'等于上⼀个⽉' 。

要使⽤⽇期动态筛选，values[]内的结构体需要指定type: DynamicSimple， 当op为equals时，dynamicType可以为如下的值（⼤⼩写不敏感） ：

• "today": 今天 • "yesterday": 昨天 • "tomorrow": 明天 • "last7Days": 最近 7 天 • "last30Days": 最近 30 天 • "thisWeek": 本周 • "lastWeek": 上周 • "nextWeek" ：下周 • "thisMonth": 本⽉ • "lastMonth": 上⽉ • "nextMonth": 次⽉ 1 2 3 4 5 6 7 8 9 10 11 Plain Text

当op为greater或less时，dynamicType只能是昨天、今天或明天。

## 附件2：PY脚本编辑器公⽹IP地址

- ⽩名单CIDR的形式：

|   Plain | Text               |
|---------|--------------------|
|       1 | 101.201.253.202/32 |
|       2 | 110.43.90.21/32    |
|       3 | 110.43.90.22/31    |
|       4 | 110.43.90.24/31    |
|       5 | 114.112.66.4/30    |
|       6 | 114.112.66.8/32    |
|       7 | 140.210.67.133/32  |
|       8 | 140.210.67.134/31  |
|       9 | 140.210.67.136/30  |
|      10 | 140.210.67.140/32  |
|      11 | 110.43.67.132/30   |
|      12 | 110.43.67.244/30   |

## · ⽩名单IP的形式：

|   JSON |                 |
|--------|-----------------|
|      1 | 101.201.253.202 |
|      2 | 110.43.90.21    |
|      3 | 110.43.90.22    |
|      4 | 110.43.90.23    |
|      5 | 110.43.90.24    |
|      6 | 110.43.90.25    |
|      7 | 114.112.66.4    |
|      8 | 114.112.66.5    |
|      9 | 114.112.66.6    |
|     10 | 114.112.66.7    |
|     11 | 114.112.66.8    |
|     12 | 140.210.67.133  |
|     13 | 140.210.67.134  |
|     14 | 140.210.67.135  |
|     15 | 140.210.67.136  |
|     16 | 140.210.67.137  |
|     17 | 140.210.67.138  |
|     18 | 140.210.67.139  |
|     19 | 140.210.67.140  |
|     20 | 110.43.67.132   |
|     21 | 110.43.67.133   |
|     22 | 110.43.67.134   |
|     23 | 110.43.67.135   |
|     24 | 110.43.67.244   |
|     25 | 110.43.67.245   |
|     26 | 110.43.67.246   |
|     27 | 110.43.67.247   |