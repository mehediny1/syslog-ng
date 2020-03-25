#!/usr/bin/env python
#############################################################################
# Copyright (c) 2015-2018 Balabit
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# As an additional exemption you are allowed to compile & link against the
# OpenSSL libraries as published by the OpenSSL project. See the file
# COPYING for details.
#
#############################################################################


class ConfigRenderer(object):
    def __init__(self, syslog_ng_config):
        self.__syslog_ng_config = syslog_ng_config
        self.__syslog_ng_config_content = ""
        self.__render()

    def get_rendered_config(self):
        return self.__syslog_ng_config_content

    def __render(self, re_create_config=None):
        if re_create_config:
            self.__syslog_ng_config_content = ""

        version = self.__syslog_ng_config["version"]
        includes = self.__syslog_ng_config["includes"]
        global_options = self.__syslog_ng_config["global_options"]
        statement_groups = self.__syslog_ng_config["statement_groups"]
        logpath_groups = self.__syslog_ng_config["logpath_groups"]

        if version:
            self.__render_version(version)
        if includes:
            self.__render_includes(includes)
        if global_options:
            self.__render_global_options(global_options)
        if statement_groups:
            self.__render_statement_groups(statement_groups)
        if logpath_groups:
            self.__render_logpath_groups(logpath_groups)

    def __render_version(self, version):
        self.__syslog_ng_config_content += "@version: {}\n".format(version)

    def __render_includes(self, includes):
        for include in includes:
            self.__syslog_ng_config_content += '@include "{}"\n'.format(include)

    def __render_global_options(self, global_options):
        globals_options_header = "options {\n"
        globals_options_footer = "};\n"
        self.__syslog_ng_config_content += globals_options_header
        for option_name, option_value in global_options.items():
            self.__syslog_ng_config_content += "    {}({});\n".format(option_name, option_value)
        self.__syslog_ng_config_content += globals_options_footer

    def __render_positional_options(self, positional_parameters):
        for parameter in positional_parameters:
            self.__syslog_ng_config_content += "        {}\n".format(str(parameter))

    def __render_driver_options(self, driver_options):
        for option_name, option_value in driver_options.items():
            if isinstance(option_value, dict):
                self.__syslog_ng_config_content += "        {}(\n".format(option_name)
                self.__render_driver_options(option_value)
                self.__syslog_ng_config_content += "        )\n"
            elif (isinstance(option_value, tuple) or isinstance(option_value, list)):
                for element in option_value:
                    self.__syslog_ng_config_content += "        {}({})\n".format(option_name, element)
            else:
                self.__syslog_ng_config_content += "        {}({})\n".format(option_name, option_value)

    def __render_statement_groups(self, statement_groups):
        for statement_group in statement_groups:
            # statement header
            self.__syslog_ng_config_content += "\n{} {} {{\n".format(
                statement_group.group_type, statement_group.group_id,
            )

            for statement in statement_group:
                # driver header
                self.__syslog_ng_config_content += "    {} (\n".format(statement.driver_name)

                # driver options
                self.__render_positional_options(statement.positional_parameters)
                self.__render_driver_options(statement.options)

                # driver footer
                self.__syslog_ng_config_content += "    );\n"

            # statement footer
            self.__syslog_ng_config_content += "};\n"

    def __render_logpath_groups(self, logpath_groups):
        for logpath_group in logpath_groups:
            self.__syslog_ng_config_content += "\nlog {\n"
            for statement_group in logpath_group.logpath:
                if statement_group.group_type == "log":
                    self.__render_logpath_groups(logpath_groups=[statement_group])
                else:
                    self.__syslog_ng_config_content += "    {}({});\n".format(
                        statement_group.group_type, statement_group.group_id,
                    )
            if logpath_group.flags:
                self.__syslog_ng_config_content += "    flags({});\n".format("".join(logpath_group.flags))
            self.__syslog_ng_config_content += "};\n"
