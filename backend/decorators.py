from container import container

def service(cls):
    container.register_class(cls)
    return cls