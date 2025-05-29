# GRPCLess 中间件

中间件是 GRPCLess 的一个重要特性，它允许你在请求处理之前或之后执行一些逻辑。中间件可以用于日志记录、身份验证、授权、错误处理等。

中间件本质是一个异步装饰器。

## 示例

以下是一个最简单的装饰器示例：

```python
def middleware(func: Callable[[Any], Any]) -> Callable:
    async def warpper(request) -> Any:
        ret = await func(request)
        return ret
    return warpper
```

其中的 request 和其返回值为对应的 pb 对象。

> 越晚注册的中间件会被包在最内层，即注册的越晚其调用会越晚，返回也越早。

## 注册

GRPCLess 对象提供了注册全局中间件的方法：

```python
app.add_middleware(middleware)
```

也可以通过在注册装饰器中使用 `middleware: list[Callable]` 参数对特定函数注册中间件。而 `use_global_middleware: bool` 参数决定是否继承全局中间件。

> 注意：全局中间件的注册只对其下方仍未被注册的函数有效。无论如何不要在任何函数已注册后注册全局中间件，这可能会导致代码难以理解。

## 内置中间件

所有内置中间件均位于 `grpcless.middleware` 中。

默认提供（注册）了以下中间件：

| 名称 | 功能 | 默认注册范围 |
| :-- | :-: | :-- |
| ErrorTraceMiddleware | 错误捕获 | 全局 |
| LogMiddleware | 带有计时的请求日志 | `request` |
| LogStreamMiddleware | 带有计时的请求日志，可记录流的开始与停止 | `stream` `clientstream` `serverstream` |

> 如果需要禁用默认注册的内置中间件，对于函数，可以在函数注册时设置 `_sys_middleware=[]`。对于默认的全局中间件，可以在 GRPCLess 初始化时设置 `global_middleware=[]`。
