# -*- coding: utf-8 -*-

import os
from config import development
from config import production
from configure_object import dict_from_model, Dict2Obj

default_env = "development"

execute_env = os.environ.get("_ENV", default_env)
ebay_env = os.environ.get("EBAY_ENV", "production")

if execute_env.lower() in ["production"]:
    config = production
else:
    config = development

settings = Dict2Obj(dict_from_model(config))
settings.configure("EBAY_ENV", ebay_env)
settings.configure("EXECUTE_ENV", execute_env)

del execute_env
del ebay_env
