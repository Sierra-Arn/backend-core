# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# app/shared/base_config.py
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
   """
   Base configuration class.

   All subclasses inherit automatic loading of settings from environment variables
   (including from a `.env` file) and support default values defined in code.
   During instantiation, values are resolved in the following order of precedence
   (from highest to lowest priority):

   1. **Explicitly passed arguments** — values provided directly to the constructor.
   2. **Environment variables** — including those loaded from the `.env` file,
   prefixed according to the subclass's `env_prefix`.
   3. **Code-defined defaults** — fallback values specified as field defaults
   in the class definition.

   Notes:
   ------
   1. Automatically loads settings from a `.env` file in the current working directory
   using a module-specific prefix specified by the subclass.

   2. Subclasses **must** define a class-level `env_prefix` string (e.g., `"API_"`).
   All environment variables for the module must start with this prefix.

   3. The `.env` file must use UTF-8 encoding. 
   4. Variable names are case-insensitive.
   5. Any extra (unrecognized) variables are silently ignored.
   6. The configuration is immutable after instantiation.
   """

   # Subclasses must override this
   env_prefix: ClassVar[str]

   def __init_subclass__(cls, **kwargs):
      super().__init_subclass__(**kwargs)
      # Dynamically set model_config based on env_prefix
      cls.model_config = SettingsConfigDict(
         env_file=".env",
         env_file_encoding="utf-8",
         case_sensitive=False,
         extra="ignore",
         frozen=True,
         env_prefix=cls.env_prefix
      )