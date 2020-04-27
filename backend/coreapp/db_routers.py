# class CoreDBRouter:
#     meta_db = 'mindfeeder_core'
#     route_to_db = 'mindfeeder_core'
#     migrations_allowed = False

#     def db_for_read(self, model, **hints):
#         # import ipdb; ipdb.set_trace()
#         if getattr(model, '_db', None) == self.meta_db:
#             return self.route_to_db
#         return None  # None means "let other routers decide (eg. default)"

#     def db_for_write(self, model, **hints):
#         if getattr(model, '_db', None) == self.meta_db:
#             return self.route_to_db
#         return None  # None means "let other routers decide (eg. default)"

#     def allow_relation(self, obj1, obj2, **hints):
#         # only objects in same db can be related
#         return getattr(obj1, '_db', -1) == getattr(obj2._meta, '_db', -2)

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         if db == self.meta_db:
#             return self.migrations_allowed
#         return None  # None means "let other routers decide
