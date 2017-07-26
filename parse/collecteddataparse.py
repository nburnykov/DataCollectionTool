import jtextfsm
import csv
from constants import PROJECTPATH
from confproc.yamlDecoder import yamlload
from typing import Optional, Dict, List



def _find_parser(cli_output_file: str, query_dict: Dict) -> Optional[List[str]]:
    for line in query_dict:
        if 'file' in line:
            if line['file'] == cli_output_file:
                if 'parsers' in line:
                    return [pr['parser'] for pr in line['parsers']]


def _parse_cli_output(cli_output_file_fullpath: str, parser_fullpath: str) -> Optional[List]:

    # TODO try finally
    with open(cli_output_file_fullpath, 'r') as cli_file:
        cli_output = cli_file.read()

    tfsm_template = open(parser_fullpath)
    re_table = jtextfsm.TextFSM(tfsm_template)
    re_table_header = re_table.header
    parsed_output = re_table.ParseText(cli_output)
    tfsm_template.close()

    return [re_table_header] + parsed_output


def collected_data_parse(scan_name: str):

    scandr = PROJECTPATH + '\\_DATA\\' + scan_name + '\\'

    # TODO try finally
    maindict = yamlload(scandr + scan_name + ".yaml")

    for dev in maindict['Discovered Data']:

        if dev['is_data_collected']:
            query_dict = yamlload(PROJECTPATH + '_DeviceQueryScripts\\' + dev['queryscript'])

            for fl in dev['filepath']:
                f = fl.split('\\')[::-1]
                parser_list = _find_parser(f[0], query_dict)

                if parser_list is not None:

                    for i, parser in enumerate(parser_list):

                        parser_fullpath = PROJECTPATH + '\\_ParseTemplates\\' + parser
                        cli_output_file_fullpath = PROJECTPATH + '_DATA\\' + fl
                        #print(dev['IP'])
                        parsed_data = _parse_cli_output(cli_output_file_fullpath, parser_fullpath)

                        if parsed_data is not None:
                            with open(cli_output_file_fullpath + '.parser_{}.csv'.format(str(i+1)), 'w', newline='') as csv_file:
                                writer = csv.writer(csv_file, delimiter=';')
                                writer.writerows(parsed_data)







