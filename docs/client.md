# GRPCLess Client 支持

GRPCLess 提供了一个适用于服务端的客户端支持，带有连接池与健康检查，可以用于与其它 grpc 服务进行通信。

## 初始化

```python
# 这里建议手动指定注解类型以便于 IDE 开发
client: grpcless.Client[test_grpc.TestServiceStub] = grpcless.Client(app,
    "127.0.0.1:50051",
    "test.proto:TestService")
```

你需要指定目标服务的地址以及服务名（服务名中不带有 `Stub` 后缀）。

`args: dict` 可用于指定连接池的详细参数。可用参数如下：

```python
pool_size: int = 10, # 池大小
health_check_interval: int = 30,  # 健康检查间隔（秒）
max_idle_time: int = 300,  # 最大空闲时间（秒）
```

## 启动

服务不需要也不能手动启动。其会随 `app.run()` 一同启动。其启动在生命周期运行前。

## 使用

```python
async with client() as stub:
    ret = await stub.YourMethod(test_pb2.Request(args))
```

其中 Method 的参数与返回值与定义一致。
