# GRPCLess 对象创建

GRPCLess 对象可采用以下代码创建：

```python
import grpcless

app = grpcless.GRPCLess(proto, "proto服务", ...)
```

> 默认对象名为 `app`，不建议修改。

## 参数列表

- `proto`: 创建的 `Proto` 对象。见 [Proto 对象](./proto.md)。
- `服务`: 服务名称，可传入多个。格式如：`文件名:服务名`。例如: `test.proto:TestService`。此处的文件名需要与 `Proto` 对象中的文件名一致。Service 后不需要加 `Base` 后缀。
- `life`: 定义生命周期，见 [生命周期](./life.md)。
- `global_middleware`: 默认的全局中间件。见 [中间件](./middleware.md)。

## 启动项目

```python
app.run("0.0.0.0", 50051)
```

也可使用命令行

```bash
grpcless run main.py:app --host 0.0.0.0 --port 50051
```

### 启动时其它参数

启动时还支持以下参数：

#### `loop`

loop 参数用于指定事件循环类型，默认为 `auto`。可选值有：

- `auto`
- `asyncio`
- `uvloop`
- `proactor`

auto 的选择逻辑如下：

- 如果 `uvloop` 模块存在，则选择 `uvloop`
- 否则如果为 Windows，则选择 `proactor`
- 否则选择 `asyncio`

本参数也可用于命令行启动。
