import logging

from tornado import web
from tornado.ioloop import PeriodicCallback
import tornado


class Application(web.Application):

    def __init__(self, settings, loop, model_routers, before_hooks=[],
        after_hooks=[], delay_tasks=[], periodic_tasks=[]):
        self.loop = loop
        self.routers = self.prefix_model_routers(model_routers)
        self.before_hooks = before_hooks
        self.after_hooks = after_hooks
        self.delay_tasks = delay_tasks
        self.periodic_tasks = periodic_tasks
        self.delay_task_runners = []
        self.periodic_task_runners = []

        if before_hooks:
            for hook in self.before_hooks:
                hook(self)

        super(Application, self).__init__(self.routers, **settings)

        if after_hooks:
            for hook in self.after_hooks:
                hook(self)
    
    def start_delay_tasks(self):
        """ 启动延时任务 """
        for delay_task in self.delay_tasks:
            self.loop.call_later(**delay_task)

    def start_periodic_tasks(self):
        """ 启动周期任务 """
        for periodic_task in self.periodic_tasks:
            self.periodic_task_runners.append(PeriodicCallback(**periodic_task))
            self.periodic_task_runners[-1].start()

    def stop_periodic_tasks(self):
        """ 停止周期任务 """
        for periodic_task_runner in self.periodic_task_runners:
            periodic_task_runner.stop()

    @classmethod
    def prefix_routers(cls, routers, prefix):
        if not prefix:
            return routers
        prefixed_routers = []
        for router in routers:
            reg_url = "/" + prefix + router[0]
            new_router = (reg_url, router[1], router[2]) if len(
                router) > 2 else (reg_url, router[1])
            prefixed_routers.append(new_router)
        return prefixed_routers

    @classmethod
    def prefix_model_routers(cls, model_routers):
        """ 为子模块路由添加前缀 """
        prefixed_routers = []
        for service_router in model_routers:
            prefixed_routers += cls.prefix_routers(**service_router)
        return prefixed_routers
