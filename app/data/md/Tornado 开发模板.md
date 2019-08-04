##Tornado 开发模板

2019-07-27 11:30:28

Github 近期推出了项目模板的功能，从模板创建新项目从未如此方便。为了方便挖坑，我也做了一个开箱即用的模板：[template-tornado](https://github.com/Jackeriss/template-tornado)。  
使用该模板可以快速搭建一个基于 tornado 的 RESTful API 服务器。  
tornado 的优点：并发性能优异，代码简洁轻量，扩展性强。  
本模板充分利用了 tornado 的这些优点，并在其基础上做了一些扩展与定制，主要功能如下：

###使用 uvloop 加速

[uvloop](https://github.com/MagicStack/uvloop) 是 asyncio 默认事件循环的一个替代品，实现的功能完整，且即插即用。uvloop 是用 Cython 写的，建于 libuv 之上。uvloop 可以使 asyncio 更快。事实上，它至少比 Node.js、gevent 和其他 Python 异步框架要快两倍。基于 uvloop 的 asyncio 速度已经接近了 Go 程序。

###使用 orjson 替代标准库 json

[orjson](https://github.com/ijl/orjson) 是 python 中最快的 json 库，其速度较标准库有显著提升。

###兼容同步函数

在写异步代码的过程中最令人头疼的事情就是有些函数和库是同步且耗时的（例如 IO 读写，requests 网络请求），阻塞了客户代码与 asycio 事件循环的唯一线程，因此在执行调用时，整个应用程序都会冻结。这个问题的解决方法是，使用事件循环对象的 `run_in_executor` 方法。asyncio 的事件循环在背后维护着一个 `ThreadPoolExecutor` 对象，我们可以调用 `run_in_executor` 方法，把可调用对象发给它执行。此功能封装在 `util/thread_pool_util.py` 中。

###参数校验

使用 [schema](https://github.com/keleshev/schema) 这个库来做参数校验。可以在 `util/schema_util.py` 中添加自定义参数校验器。

###Basic-Info 与协程上下文

推荐尽量不使用 cookie，一些通用信息（例如客户端类型等）前端可以放在 `Basic-Info` 这个 Header 中，后端可以将通用信息放在 `aiotask_context` 协程上下文中。

###全局异常处理

在 `hook/before_hook.py` 中为所有 handler 的请求方法添加了异常处理装饰器。每个可处理的异常都要定义 code、message 和 status 三个属性。

###后台延时任务与周期任务

服务启动后如果有一些后台任务需要执行可以写在 `tasks` 文件夹中。如果只需要执行一次，那它就是一个 `delay_task`，如果需要周期性的执行则是 `periodic_task`。

###本地缓存

`util/cache_util.py` 中实现了一个本地缓存装饰器，它可以为任意函数设置本地缓存，并且支持设置过期时间。这个缓存自动过期的功能就是通过上面提到的周期任务实现的。

###超时日志

`util/time_util.py` 中有一个打印函数超时日志的装饰器，如有需要可接入 [sentry](https://github.com/getsentry/sentry) 进行日志报警监控。

###HTTP 客户端、Redis 连接池 以及 PG 连接池等

常用的数据源连接已经封装好了，其中 Redis 和 PG 客户端默认是不会加载的，需要用的时候把 `Pipfile` 相应的库取消注释重新安装一下。然后改一下对应的 yaml 配置文件，最后将 `main.py` 的 `AFTER_HOOKS` 中的初始化方法取消注释就行了。

###依赖管理与启动方法

本模板使用 [pipenv](https://github.com/pypa/pipenv) 来管理依赖和执行启动命令。

第一步，初始化虚拟环境并安装依赖：
执行 `pipenv install`

第二步，启动服务：
如果是本地开发环境运行则执行 `pipenv run serve`
使用该方法启动程序会在前台运行并在终端窗口输出日志，由于使用 asyncio 代替了 IOLoop，即使在 debug 模式下修改代码也不会自动重启。

如果是非本地开发、测试、预发或生产环境，则执行 `pipenv run restart [dev|test|pre|prod]`，使用该方法启动程序会在后台运行，并将日志输出在 `/app/log/` 文件夹下，如果启动失败可能是没有该日志路径的写权限，修改路径权限后重试即可。你也可以通过修改 `app.sh` 文件来自定义启动脚本。限后重试即可。你也可以通过修改 `app.sh` 文件来自定义启动脚本。

执行 `pipenv run log [dev|test|pre|prod]` 可以打印实时日志。