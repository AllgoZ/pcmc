class HpRouter:
    """
    A router to control all database operations for models in the hp and goi apps.
    """

    def db_for_read(self, model, **hints):
        """
        Directs read operations for hp and goi models to their respective databases.
        """
        if model._meta.app_label == 'hp':
            return 'hp_db'
        elif model._meta.app_label == 'goi':
            return 'goi_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Directs write operations for hp and goi models to their respective databases.
        """
        if model._meta.app_label == 'hp':
            return 'hp_db'
        elif model._meta.app_label == 'goi':
            return 'goi_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects belong to the same app or to different apps.
        """
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure models are migrated only to their respective databases.
        """
        if app_label == 'hp':
            return db == 'hp_db'
        elif app_label == 'goi':
            return db == 'goi_db'
        return db == 'default'
