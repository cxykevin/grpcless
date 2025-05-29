# GRPCLess fix 的 builtins

## `print()`

时机：`app.run()` 即服务启动时

重载了默认的 print 函数，使其符合日志格式。默认类型为 `DEBUG`。
