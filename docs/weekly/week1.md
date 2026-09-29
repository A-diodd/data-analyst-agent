# 第一周

## 自己的理解：

先解释各个创建的文件是什么含义，首先是data文件夹，里面装的是巴西销售数据的原始数据，这些数据已经成功通过db脚本传输到我的postgressql数据库里了，数据库的名字叫做olist。
接着是eval文件夹，里面有自己手工写好的真的现象文件，这个应该是后续自己看这个数据表然后写进去自己的观察。然后里面还有profile_truth这个文件，这里面显示了我用sql查询得到的一些数据信息特征。
然后是runs文件夹，这里面之后可能会写我的智能体在运行时执行的各个阶段的信息
然后是semantic文件夹，这里我的metrics指标用来表示各个指标的含义精确表示，为了后续测评的时候能统一口径，避免评测标准不统一
然后是sql文件夹，这里面两个.sql文件写了数据库命令，schema来写创建这个数据库和里面九个表单的具体字段名字的类型，roles用来指定两个账户的的权限，分别是只读和可写的两个账户权限。
接着是src，这里是我的程序代码，后续用来跑我的智能体。
接着是tests文件夹，目前对两个数据库用户权限进行了测试。
最后还有docker-compose文件，应该是docker启动之后读取这个配置文件用来控制我的数据库olist。

## 数据

order_items 一行是一件商品，一个订单可以有多行。customer_id 不是一个人，同一个人看 customer_unique_id。order_items 和 payments 按 order_id 直接 JOIN，商品金额会从 13591643.70 变成 14209115.34。geolocation 按邮编前缀 JOIN 也会把行数放大很多。

## 账号

Agent 以后只用 analyst_ro。postgres 能删库，不能给它。app_rw 只写 app schema，不写业务表。

## 口径和评测

metrics.yaml 统一的是指标定义。profile_truth.yaml 记录的是数据问题，后面用来给体检 Agent 对答案。这两份文件不能混。