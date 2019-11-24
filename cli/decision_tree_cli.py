import re
from typing import Tuple, Sequence, Dict
from utils.cli_query_tree import find_attr_by_name
from devproc.connect_device import DeviceConnection
import logging

logger = logging.getLogger('main')


class DecisionTreeCLI:
    def __init__(self, connection: DeviceConnection, tree_dict: dict, do_not_disconnect=True) -> None:
        self.query_tree = tree_dict['queriesCLI']
        self._process_log = []
        self._saved_query_result = {}
        self._path_list = []
        self._tree_config_error = False
        self._target_class_list = []
        self._current_class = 'None'
        self._test_string = ''
        self._dev_conn = connection

        self._decision_tree_walk('clMainClass', tree_dict)
        if not do_not_disconnect:
            connection.disconnect()

    def _decision_tree_walk(self, current_class, tree):

        if current_class not in tree:
            self._process_log_add("Target class {} is not found".format(current_class))
            self._tree_config_error = True
            return

        dt = tree[current_class]
        self._path_list.append((dt['folder'], dt['genericscript']))
        self._test_string += dt['folder'] + " "
        self._target_class_list.append(current_class)
        self._current_class = current_class

        if 'query' in dt:

            q = dt.get('query')

            if q not in self._saved_query_result:
                self._process_log_add(f"{q} result is not found in cache, performing cli command:")
                self._process_log_add(f"Host: {self._dev_conn.ip}")

                is_attr_presented, q_list = find_attr_by_name(self.query_tree, q)
                if not is_attr_presented:
                    self._process_log_add(f"Cannot find \"{q}\" in queries list, please check decision_tree_cli.yaml")
                    self._tree_config_error = True
                    return

                output = ''
                for s in q_list:
                    output += self._dev_conn.run_command(s)

                self._saved_query_result[q] = output

            if 'parse' not in dt:
                self._process_log_add(f"\"query\" section exists but \"parse\" is not presented, "
                                      f"use current folder \"{dt['folder']}\" and script \"{dt['genericscript']}\"")
                self._tree_config_error = True
                return

            pq = dt['parse']

            target_class_list = []

            self._process_log_add(
                f"Content of the current query {q} in cache:\n===\n{self._saved_query_result[q]}\n===\n")

            for pqi in pq:

                expr = pqi['expression']
                if type(expr) is str:
                    expr = [expr]
                is_expr_found = False

                for e in expr:

                    regexp = re.compile(e, re.IGNORECASE)
                    self._process_log_add("Expression \"" + e + "\":")
                    if len(regexp.findall(self._saved_query_result[q])) > 0:
                        is_expr_found = True

                if is_expr_found:
                    target_class_list.append(pqi['targetClass'])
                    self._process_log_add("Found, proceed to next class: {}\n".format(pqi['targetClass']))
                else:
                    self._process_log_add("Not found\n")

            if len(target_class_list) == 0:
                self._process_log_add(
                    f"Expressions aren't found, \
                    using current folder \"{dt['folder']}\" and script \"{dt['genericscript']}\"")
                return

            for target_class in target_class_list:
                self._decision_tree_walk(target_class, dt)

        else:
            self._process_log_add(f"Query section is not presented, stopping recursive search, "
                                  f"using current folder \"{dt['folder']}\" and script \"{dt['genericscript']}\"")

    def _process_log_add(self, msg, c_class=''):
        if c_class == '':
            c_class = self._current_class
        self._process_log.append((self._dev_conn.ip, c_class, msg))
        return

    def get_path_list(self) -> Sequence[Tuple[str, str]]:
        return self._path_list

    def dump_log(self):
        for line in self._process_log:
            logger.debug(f'{line[0]} {line[1]} {line[2]}')

    def is_tree_config_error(self) -> bool:
        return self._tree_config_error

    def get_target_class_list(self) -> Sequence[str]:
        return self._target_class_list

    def get_test_string(self) -> str:
        return str(self._test_string).strip(' ')

    def get_cached_query_result(self) -> Dict[str, str]:
        return self._saved_query_result
