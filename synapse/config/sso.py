# -*- coding: utf-8 -*-
# Copyright 2020 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pkg_resources
from typing import Any, Dict, Optional

from ._base import Config, ConfigError


class SSOConfig(Config):
    """SSO Configuration
    """
    section = "sso"

    def read_config(self, config, **kwargs):
        sso_config = config.get("sso", None)  # type: Optional[Dict[str, Any]]
        if sso_config:
            self.sso_redirect_confirm_enabled = sso_config.get(
                "redirect_confirm_enabled", False,
            )

            if self.sso_redirect_confirm_enabled and "public_baseurl" not in config:
                raise ConfigError(
                    "Can't set up redirect confirmation without 'public_baseurl'"
                )

            template_dir = config.get("template_dir")

            if not template_dir:
                template_dir = pkg_resources.resource_filename("synapse", "res/templates")

            self.sso_redirect_confirm_template_dir = template_dir
            self.sso_redirect_confirm_template_file = config.get(
                "redirect_confirm_template", "sso_redirect_confirm.html",
            )
        else:
            self.sso_redirect_confirm_enabled = False

    def generate_config_section(self, **kwargs):
        return """
        # Settings to use when using SSO (Single Sign-On).
        #
        #sso:
        #   # Whether to add an extra step to the login flow before redirecting to the
        #   # client after a successful login, to ask the user to confirm where they want
        #   # to be redirected to.
        #   #
        #   redirect_confirm_enabled: true
        #
        #   # The directory in which to find the template to serve in that extra
        #   # confirmation step.
        #   # Defaults to res/templates.
        #   #
        #   template_dir: "res/templates"
        #
        #   # The template to serve in that extra confirmation step.
        #   # When rendering, this template is given two variables:
        #   #   * redirect_url: the URL the user is about to be redirected to, or an
        #   #                   empty string if none was provided in the request.
        #   #   * server_name: the homeserver's name.
        #   # See res/templates/sso_redirect_confirm.html for an example of how to use
        #   # them.
        #   # Defaults to sso_redirect_confirm.html.
        #   #
        #   redirect_confirm_template: "sso_redirect_confirm.html"
        """
