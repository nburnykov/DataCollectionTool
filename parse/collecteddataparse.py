import jtextfsm
import csv
import parse.postpocessors
from constants import PROJECTPATH, DATADIR
from confproc.fileProc import yaml_load
from typing import Optional, Dict, List, Tuple
from database.dbhandler import DataBaseHandler
import logging

logger = logging.getLogger('main')


def _find_parser(cli_output_file: str, query_dict: Dict) -> List[Dict]:
    res_list = []
    for line in query_dict:
        if 'file' in line:
            if line['file'] == cli_output_file:
                if line.get('parsers') is not None:
                    for pr in line['parsers']:
                        res_list.append(pr)
    return res_list


def _get_postprocessors(parser_dict: Dict) -> List[Tuple[str, List[str]]]:
    res_list = []
    if parser_dict.get('postprocess') is not None:
        for pp in parser_dict['postprocess']:
            if 'column' and 'processors' in pp:
                proc = [str(p).strip() for p in str(pp['processors']).split(',')]
                vproc = [p for p in proc if hasattr(parse.postpocessors, p)]
                res_list.append((pp['column'], vproc))
    return res_list


def _apply_postprocessors(processor_list: List[Tuple[str, List[str]]], parsed_data: List) -> List:
    for proc in processor_list:
        column_name = proc[0]
        index = 0
        for i, column in enumerate(parsed_data[0]):
            if column == column_name:
                index = i
                break
        else:
            continue
        processors = proc[1]
        for parsed_str in parsed_data[1:]:
            for p in processors:
                parsed_str[index] = getattr(parse.postpocessors, p)(parsed_str[index])
    return parsed_data


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

    scandr = PROJECTPATH + '\\' + DATADIR + '\\' + scan_name + '\\'

    # TODO try finally
    maindict = yaml_load(scandr + scan_name + ".yaml")

    dbh = DataBaseHandler(scandr + scan_name + ".db")

    for dev in maindict['Discovered Data']:

        if dev['is data collected']:
            query_dict = yaml_load(PROJECTPATH + '_DeviceQueryScripts\\' + dev['queryscript'])

            for fl in dev['filepath']:
                f = fl.split('\\')[::-1]
                parser_list = _find_parser(f[0], query_dict)

                if len(parser_list) > 0:

                    for i, parser in enumerate(parser_list):

                        parser_fullpath = PROJECTPATH + '\\_ParseTemplates\\' + parser['parser']
                        cli_output_file_fullpath = PROJECTPATH + '_DATA\\' + fl
                        parsed_data = _parse_cli_output(cli_output_file_fullpath, parser_fullpath)

                        if parsed_data is not None:
                            processor_list = _get_postprocessors(parser)
                            if len(processor_list) > 0:
                                parsed_data = _apply_postprocessors(processor_list, parsed_data)

                            if parser.get('table') is not None:
                                logger.debug(parsed_data[0])
                                [logger.debug(line) for line in parsed_data[1:]]
                                dbh.add_data(parser['table'], parsed_data[0], parsed_data[1:], dev['IP'])

                            with open(cli_output_file_fullpath + '.parser_{}.csv'.format(str(i+1)),
                                      'w', newline='') as csv_file:
                                writer = csv.writer(csv_file, delimiter=';')
                                writer.writerows(parsed_data)

    dbh.disconnect()
    logger.debug('Finish load data to DB')







