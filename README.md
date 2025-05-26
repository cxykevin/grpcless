# grpcless

> 一个快速的 智能的 基于 grpclib 的 Python grpc 框架

## 快速上手

### 安装

```bash
pip install grpcless
```

> 生产模式下运行时无需包含本包，仅包含 `grpclib` 作为其依赖即可。生产模式下会自动创建一个同名的静态包。

本包仅在 `Python 3.13 Linux` 上进行过测试。不保证其在 `3.12-` 的可用性。

### 最小示例

#### 文件结构

```text
test 
├── proto
│   └── test.proto
└── test.py
```

#### 创建示例 Proto 文件

`proto/test.proto`

```protobuf
syntax = "proto3";
package test;
// 定义服务，包含四种 RPC 方法类型
service TestService {
  // 普通 RPC：客户端发送一个请求，服务器返回一个响应
  rpc SimpleMethod(Request) returns (Response) {}
  // 服务器流式 RPC：客户端发送一个请求，服务器返回一个流式响应
  rpc ServerStreamingMethod(Request) returns (stream Response) {}
  // 客户端流式 RPC：客户端发送流式请求，服务器返回一个响应
  rpc ClientStreamingMethod(stream Request) returns (Response) {}
  // 双向流式 RPC：客户端和服务器都可以发送流式消息
  rpc BidirectionalStreamingMethod(stream Request) returns (stream Response) {}
}
// 消息嵌套
message InnerMsg { int32 value = 1; }
// 请求消息
message Request {
  // 整数类型
  int32 int32_value = 1;
  int64 int64_value = 2;
  // 二进制数据
  bytes bytes_value = 3;
  // 字符串 (用于 map 的 key)
  string name = 4;
  InnerMsg a = 5;
}
// 响应消息
message Response {
  // 状态码
  int32 status_code = 1;
  // 消息
  string message = 2;
  // 二进制数据
  bytes data = 3;
}
```

#### 创建代码

`test.py`

```python
import grpcless # 引入包

import test_pb2 # 直接使用 import 引入 pb
# 注意：任何结尾为 _pb2 或者为 _grpc 的包都会被自动识别为生成的 protobuf 包
# 在自己的代码中请勿使用以上后缀结尾
# 这类包请在引入 grpcless 后进行引入，其导入会被推迟到 Proto 对象创建

proto = grpcless.Proto("test.proto", # 在此处可引入多个 .proto 文件
                       proto_path="./proto") # 引入 Proto 文件
# 在引入时会自动对 proto 文件进行编译
# 请勿创建多个 Proto 对象！
# 其它参数：
#     output_dir: str = 'pb' # 编译产物文件夹
#     other_include: list[str] = [] # 其它导入列表


# 生命周期定义
async def life(*args,**kwargs):
    # your_code
    yield
    # 由于没有实现拦截信号，这里的代码暂时不会执行
# 在 GRPCLess 中指定 life 参数即可

# 定义服务
app = grpcless.GRPCLess(proto, "test.proto:TestService") # 这里可一次引入多个服务


# 这里可以定义全局中间件，中间件本质上是一个装饰器
def middleware(func: Callable[[Any], Any]) -> Callable:
    async def warpper(request) -> Any: # 注意中间件处理的是请求对象而不是流
        # tips: 如果需要直接对流进行处理可以注册为 grpclib 中间件
        print("Middleware called! ")
        ret = await func(request)
        return ret
    return warpper
# app.add_middleware(middleware)
# 越晚被注册的中间件会在越内层运行

# 一元请求
# 如果具有多个 Service，请使用 Service:function 的形式
@app.request("SimpleMethod")
# 暂时只支持异步函数
async def simple_method(int32_value: int, int64_value: int,
                        bytes_value: bytes, name: str):
    # pb 文件中的参数会被自动展开（仅展开一层）
    print("simple_method", int32_value, int64_value, bytes_value, name)
    return { # 以字典形式返回值，注意也只展开一层
        "status_code": 114514,
        "a": test_pb2.InnerMsg( # 对于嵌套消息仍旧需要手动构建
            value=1
        )
    }

# 服务端流
@app.client_stream("ClientStreamingMethod")
async def clistream_method(stream: grpcless.Stream):
    async for request in stream: # 使用 async for 语法接受消息
        # 也支持使用 recv_message
        print(request)
        if (request.int32_value == 1):
            break
    return {"status_code": 114514}

# 客户端流
@app.server_stream("ServerStreamingMethod")
async def serverst_method(stream: grpcless.Stream, int32_value: int, int64_value: int,
                          bytes_value: bytes, name: str):
    # 对于流对象，名称请使用固定的 stream
    await stream.send_message({"status_code": 1234}) # 只展开一层

# 双向流
@app.stream("BidirectionalStreamingMethod")
async def stream_method(stream: grpcless.Stream):
    async for request in stream:
        print(request)
        if (request.int32_value == 1):
            break
        await stream.send_message({"status_code": 1234})

# 运行服务器
if __name__ == "__main__":
    app.run("0.0.0.0", 50051)
```

> 如果需要返回错误，请使用 `grpclib` 相关的 exception。

#### 启动服务器

```bash
python test.py
# 或者
grpcless run test.py:app --host 0.0.0.0 --port 50051
```

#### 运行后的文件结构

```text
test 
├── pb 默认的编译产物文件夹
│   ├── .grpcEcache 编译缓存，记录修改时间
│   ├── test_pb2.py 编译产物
│   ├── test_pb2.pyi
│   └── .test_grpc.py
├── proto
│   └── test.proto
└── test.py
```

#### 生成生产代码

```bash
grpcless build test.py:app test.py # 这里可以补充其它源文件
```

> 生产模式的代码会去除所有动态部分，以便于更好进行静态优化

### 局限

- 目前未实现证书相关的导入，暂时不支持 GRPC TLS（待办）
- 目前未实现日志的存储以及异步优化（待办）
- 不能导入复杂的 .proto 文件
- 缺少优化相关的类型注解

### 对比

|  | grpcless | fast-grpc | grpclib | grpcio  |
| :-- | :-: | :-: | :-: | :-: |
| 写法 | 装饰器 | 装饰器 | 类 | 类 |
| API范式 | API优先 | 代码优先 | API优先 | API优先 |
| 异步 | 是 | 否 | 是 | 否 |
| 性能侧重 | IO密集 | CPU密集 | IO密集 | CPU密集 |
| 自动 Proto 编译 | 支持 | 支持 | 不支持 | 不支持 |
| 日志友好 | 是 | 否 | 否 | 否 |
| TLS支持 | 不支持 | 支持 | 支持 | 支持 |
| 命令行工具 | 有 | 无 | 无 | 无 |
| 自动重载 | 不支持 | 不支持 | 不支持 | 不支持 |
| 静态支持 | 支持i | 不支持 | 支持 | 支持 |

> [i] 仅限生产模式下
