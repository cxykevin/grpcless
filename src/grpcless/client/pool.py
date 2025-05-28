import asyncio
import time
from .. import log
from typing import Dict, Optional, Set
from grpclib.client import Channel
from grpclib.health.v1.health_pb2 import HealthCheckRequest
from grpclib.health.v1.health_grpc import HealthStub
from grpclib.exceptions import GRPCError
from contextlib import asynccontextmanager


class PoolObj:
    def __init__(self,
                 host: str,
                 port: int,
                 pool_size: int = 10,
                 health_check_interval: int = 30,  # 健康检查间隔（秒）
                 max_idle_time: int = 300,  # 最大空闲时间（秒）
                 enable_health_check: bool = True,
                 health_check_service: str = ""):  # 健康检查服务名
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.health_check_interval = health_check_interval
        self.max_idle_time = max_idle_time
        self.enable_health_check = enable_health_check
        self.health_check_service = health_check_service

        self._pool = asyncio.Queue(maxsize=pool_size)
        self._created_connections = 0
        self._lock = asyncio.Lock()

        # 健康检查相关
        self._connection_metadata: Dict[int, Dict] = {}  # 连接元数据
        self._unhealthy_connections: Set[int] = set()  # 不健康的连接ID
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def start(self):
        """启动连接池和健康检查"""
        self._is_running = True
        if self.enable_health_check:
            self._health_check_task = asyncio.create_task(
                self._health_check_loop())
        log.log_client(0,
                       f"Started pool {self.host}:{self.port}")

    async def _create_connection(self) -> Channel:
        """创建新连接"""
        channel = Channel(host=self.host, port=self.port)
        connection_id = id(channel)

        # 记录连接元数据
        self._connection_metadata[connection_id] = {
            'created_at': time.time(),
            'last_used': time.time(),
            'last_health_check': 0,
            'health_check_failures': 0,
            'is_healthy': True
        }

        log.log_client(0, f"Created new connection {connection_id}")
        return channel

    async def _health_check_connection(self, connection: Channel) -> bool:
        """检查单个连接的健康状态"""
        connection_id = id(connection)

        try:
            # 使用gRPC健康检查协议
            health_stub = HealthStub(connection)
            request = HealthCheckRequest(service=self.health_check_service)

            # 设置超时时间
            response = await asyncio.wait_for(
                health_stub.Check(request),
                timeout=5.0
            )

            # 检查响应状态
            is_healthy = response.status == 1  # SERVING = 1

            # 更新元数据
            if connection_id in self._connection_metadata:
                metadata = self._connection_metadata[connection_id]
                metadata['last_health_check'] = time.time()
                metadata['is_healthy'] = is_healthy

                if is_healthy:
                    metadata['health_check_failures'] = 0
                    self._unhealthy_connections.discard(connection_id)
                else:
                    metadata['health_check_failures'] += 1
                    self._unhealthy_connections.add(connection_id)

            return is_healthy

        except asyncio.TimeoutError:
            log.log_error(
                f"Health check timeout for connection {connection_id}")
            return False
        except GRPCError as e:
            log.log_error(
                f"Health check GRPC error for connection {connection_id}: {e}")
            return False
        except Exception as e:
            log.log_error(
                f"Health check error for connection {connection_id}: {e}")
            return False

    async def _health_check_loop(self):
        """健康检查循环"""
        while self._is_running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
                await self._cleanup_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.log_error(f"Health check loop error: {e}")

    async def _perform_health_checks(self):
        """执行健康检查"""
        if self._pool.empty():
            return

        # 临时存储连接进行健康检查
        connections_to_check = []
        healthy_connections = []

        # 从池中取出所有连接进行检查
        while not self._pool.empty():
            try:
                connection = self._pool.get_nowait()
                connections_to_check.append(connection)
            except asyncio.QueueEmpty:
                break

        # 并发执行健康检查
        health_check_tasks = []
        for connection in connections_to_check:
            task = asyncio.create_task(
                self._check_and_categorize_connection(connection))
            health_check_tasks.append(task)

        if health_check_tasks:
            results = await asyncio.gather(*health_check_tasks, return_exceptions=True)

            for connection, result in zip(connections_to_check, results):
                if isinstance(result, Exception):
                    # 将连接标记为不健康
                    self._unhealthy_connections.add(id(connection))
                    connection.close()
                    await self._remove_connection_metadata(connection)
                elif result:  # 连接健康
                    healthy_connections.append(connection)
                else:  # 连接不健康
                    connection.close()
                    await self._remove_connection_metadata(connection)

        # 将健康的连接放回池中
        for connection in healthy_connections:
            try:
                self._pool.put_nowait(connection)
            except asyncio.QueueFull:
                # 如果池满了，关闭多余的连接
                connection.close()
                await self._remove_connection_metadata(connection)

    async def _check_and_categorize_connection(self, connection: Channel) -> bool:
        """检查连接并分类"""
        connection_id = id(connection)

        # 检查连接是否过于空闲
        if connection_id in self._connection_metadata:
            metadata = self._connection_metadata[connection_id]
            current_time = time.time()

            # 如果连接空闲时间过长，直接关闭
            if current_time - metadata['last_used'] > self.max_idle_time:
                return False

        # 执行健康检查
        return await self._health_check_connection(connection)

    async def _cleanup_connections(self):
        """清理不健康和过期的连接"""
        current_time = time.time()
        connections_to_remove = []

        for connection_id, metadata in list(self._connection_metadata.items()):
            # 清理长时间未使用的连接元数据
            if current_time - metadata['last_used'] > self.max_idle_time * 2:
                connections_to_remove.append(connection_id)

        # 清理元数据
        for connection_id in connections_to_remove:
            if connection_id in self._connection_metadata:
                del self._connection_metadata[connection_id]
            self._unhealthy_connections.discard(connection_id)

    async def _remove_connection_metadata(self, connection: Channel):
        """移除连接元数据"""
        connection_id = id(connection)
        if connection_id in self._connection_metadata:
            del self._connection_metadata[connection_id]
        self._unhealthy_connections.discard(connection_id)

        async with self._lock:
            self._created_connections -= 1

    async def _get_connection(self) -> Channel:
        """获取连接"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 尝试从池中获取连接（非阻塞）
                connection = self._pool.get_nowait()
                connection_id = id(connection)

                # 检查连接是否健康
                if connection_id not in self._unhealthy_connections:
                    # 更新最后使用时间
                    if connection_id in self._connection_metadata:
                        self._connection_metadata[connection_id]['last_used'] = time.time(
                        )
                    return connection
                else:
                    # 连接不健康，关闭并重试
                    connection.close()
                    await self._remove_connection_metadata(connection)
                    retry_count += 1
                    continue

            except asyncio.QueueEmpty:
                # 如果池为空，检查是否可以创建新连接
                async with self._lock:
                    if self._created_connections < self.pool_size:
                        self._created_connections += 1
                        return await self._create_connection()

                # 如果达到最大连接数，等待可用连接
                try:
                    connection = await asyncio.wait_for(self._pool.get(), timeout=10.0)
                    connection_id = id(connection)

                    # 检查连接健康状态
                    if connection_id not in self._unhealthy_connections:
                        if connection_id in self._connection_metadata:
                            self._connection_metadata[connection_id]['last_used'] = time.time(
                            )
                        return connection
                    else:
                        connection.close()
                        await self._remove_connection_metadata(connection)
                        retry_count += 1
                        continue

                except asyncio.TimeoutError:
                    raise Exception("Timeout waiting for available connection")

        raise Exception(
            f"Failed to get healthy connection after {max_retries} retries")

    async def _return_connection(self, connection: Channel):
        """归还连接"""
        connection_id = id(connection)

        # 检查连接是否健康
        if connection_id in self._unhealthy_connections:
            connection.close()
            await self._remove_connection_metadata(connection)
            return

        try:
            self._pool.put_nowait(connection)
        except asyncio.QueueFull:
            # 如果队列满了，关闭连接
            connection.close()
            await self._remove_connection_metadata(connection)

    @asynccontextmanager
    async def get_connection(self):
        """获取连接的上下文管理器"""
        connection = await self._get_connection()
        try:
            yield connection
        except Exception as e:
            # 如果使用连接时出错，标记为不健康
            connection_id = id(connection)
            self._unhealthy_connections.add(connection_id)
            raise
        finally:
            await self._return_connection(connection)

    async def get_pool_stats(self) -> Dict:
        """获取连接池统计信息"""
        return {
            'pool_size': self.pool_size,
            'created_connections': self._created_connections,
            'available_connections': self._pool.qsize(),
            'unhealthy_connections': len(self._unhealthy_connections),
            'total_connections_metadata': len(self._connection_metadata),
            'health_check_enabled': self.enable_health_check
        }

    async def close(self):
        """关闭连接池"""
        self._is_running = False

        # 停止健康检查任务
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # 关闭所有连接
        while not self._pool.empty():
            try:
                connection = self._pool.get_nowait()
                connection.close()
            except asyncio.QueueEmpty:
                break

        # 清理元数据
        self._connection_metadata.clear()
        self._unhealthy_connections.clear()
        self._created_connections = 0
