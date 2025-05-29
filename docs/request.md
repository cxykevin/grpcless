# GRPCLess 请求注册

一个请求可以简单使用如下方法注册：

```python
@app.request("SimpleMethod")
async def simple_method(...):
    return {
        ...
    }
```

## 请求名称

若只有一个 Service，则请求名称与 proto 文件中名称一致。

若存在多个 Service，以如下形式定义：

`Service:Method`

## 请求类型

### 一元请求

使用装饰器 `app.request`。

函数参数列表同 proto 文件中定义，例如：

```python
@app.request("SimpleMethod")
async def simple_method(int32_value: int, int64_value: int,
                        bytes_value: bytes, name: str):
    return {"status_code": 114514}
```

> 参数名称需要与 proto 一致。类型不必一致（不会自动进行类型转换）。

对应的 proto:

```proto
service TestService {
  ...
  rpc SimpleMethod(Request) returns (Response) {}
  ...
}

message Request {
  int32 int32_value = 1;
  int64 int64_value = 2;
  bytes bytes_value = 3;
  string name = 4;
}
message Response {
  int32 status_code = 1;
}
```

对于嵌套的消息，其不会解包。如：

```python
@app.request("SimpleMethod")
async def simple_method(...,msg: test_pb2.InnerMsg):
    ...
```

其返回值为一个字典。但嵌套消息请返回其原始对象。如：

```python
return {"status_code": 114514, "msg": test_pb2.InnerMsg()}
```

### 双向流式请求

使用装饰器 `app.stream`。

```python
@app.stream("StreamMethod")
async def stream_method(stream: grpcless.Stream):
    async for request in stream:
        # your_code
    await stream.send_message({"status_code": 1234})
```

其中 request 为其原始对象。send_message 为发送消息方法，其为一个字典，其嵌套消息不会被转换（同上文一元请求的返回）。

### 服务端流式请求

使用装饰器 `app.serverstream`。

```python
@app.serverstream("ServerStreamingMethod")
async def serverstream_method(stream: grpcless.Stream, int32_value: int, ...):
    ...
```

其中接受流的名称必须为 `stream`。

### 客户端流式请求

使用装饰器 `app.clientstream`。

```python
@app.clientstream("ClientStreamingMethod")
async def clientstream_method(stream: grpcless.Stream):
    ...
```

其返回值与一元请求一致。

## Stream 对象

Stream 对象可以被 `async for` 迭代接受消息，也可使用 `await stream.send_message()` 发送消息。
