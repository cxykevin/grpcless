# GRPCLess 生命周期

生命周期可使用以下方式定义：

```python
async def life(*args,**kwargs):
    # before code
    yield
    # after code
```

## 注册

可以在 GRPCLess 对象创建时使用 `life` 参数注册：

```python
app = grpcless.GRPCLess(...,life=life)
```
