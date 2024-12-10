"""
给朝代的官职加官职id

思路：
1. 根据朝代表DYNASTIES.txt，生成dy_dic[朝代id]=朝代名
2. 根据官职表OFFICE_CODES.txt、dy_dic，生成office_dic[朝代名]=官职列表
3. 官职匹配，加官职id：根据office_dic，将input.txt中的官职加上官职id、匹配类型，输出为output.txt
"""

# pip install char-converter

import csv

office_altname_index = 5
office_name_index = 3
office_dy_index = 1
office_id_index = 0
input_dy_index = 1


class FileOperation:
    @staticmethod
    def read_dy(file_name):
        # 朝代名为 id
        output_dic = {}
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            for row in csv_reader:
                if use_char_function:
                    row = [converter.convert(i) for i in row]
                output_dic[row[0]] = row[2]
        return output_dic

    @staticmethod
    def read_office(file_name, dy_dic):
        # output_dic 的数据结构是：以朝代名中文作为 index，value
        # 是 office 中的一个 row
        output_dic = {}
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            for row in csv_reader:
                if use_char_function:
                    row = [converter.convert(i) for i in row]
                    # if ; or ； in row[office_altname_index], split it. The condition must be in one if
                if len(row[office_altname_index]) > 1:
                    if "；" in row[office_altname_index]:
                        row[office_altname_index] = row[office_altname_index].replace(
                            "；", ";"
                        )
                    if ";" in row[office_altname_index]:
                        altname_list = row[office_altname_index].split(";")
                        altname_list = [i.replace(" ", "") for i in altname_list]
                    else:
                        altname_list = [row[office_altname_index]]
                    for altname in altname_list:
                        new_row = row.copy()
                        new_row[office_name_index] = altname
                        dy = dy_dic[row[office_dy_index]]
                        if dy not in output_dic:
                            output_dic[dy] = [new_row]
                        else:
                            output_dic[dy].append(new_row)
                dy = dy_dic[row[office_dy_index]]
                if dy not in output_dic and len(row[office_name_index]) > 1:
                    output_dic[dy] = [row]
                elif len(row[office_name_index]) > 1:
                    output_dic[dy].append(row)
                else:
                    pass
        for dy, row in output_dic.items():
            output_dic[dy] = sorted(
                output_dic[dy], key=lambda x: len(x[office_name_index]), reverse=True
            )
        return output_dic

    @staticmethod
    def read_input(file_name):
        output = []
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            for row in csv_reader:
                if use_char_function:
                    row = [converter.convert(i) for i in row]
                if len(row[input_dy_index]) > 0:
                    output.append(row)
        return output


# 性能优化：生成code_data & 写入到txt
# add xiujunhan 2023-08-22
def code_data_and_write(file_name, data_list, office_dic):
    output = []
    file = open(file_name, "w", encoding="utf-8")
    header = [
        "office_id",
        "office_name",
        "office_dy",
        "cbdb_office_id",
        "cbdb_office_name",
        "match_type",
    ]
    file.write("\t".join(header) + "\n")
    for line in data_list:
        # cbdb_office_id = "unknown"
        office_id = line[0]
        office_dy = line[input_dy_index]
        office_name = line[2]
        if office_dy in office_dic:
            for cbdb_office_item in office_dic[office_dy]:
                code_status = ""
                cbdb_office_item_name_chn = cbdb_office_item[office_name_index]
                cbdb_office_item_name_id = cbdb_office_item[office_id_index]
                if office_name == cbdb_office_item_name_chn:
                    code_status = "exact"
                elif cbdb_office_item_name_chn in office_name and cbdb_office_item_name_chn != "":
                    code_status = "partial"
                if code_status != "":
                    cbdb_office_id = cbdb_office_item_name_id
                    output_row = [
                        office_id,
                        office_name,
                        office_dy,
                        cbdb_office_id,
                        cbdb_office_item_name_chn,
                        code_status,
                    ]
                    output.append(output_row)
                    file.write("\t".join(output_row) + "\n")
                    break
            # write unknown
            if code_status == "":
                output_row = [office_id, office_name, office_dy, "unknown", "unknown", "unknown"]
                output.append(output_row)
                file.write("\t".join(output_row) + "\n")
    file.close()
    return output


# 未來可以嘗試實現：
# 1，帶上允許時間限制的條件；
#
# 2，如果有多項匹配，優先選擇有坐標信息的。
# （當前可以透過工程來實現這一點：把 ADDRESSES 按照 id 和 坐標（坐標由大到小）排序。坐標有值的排在前面

# use_char_function = False
use_char_function = True
if use_char_function:
    from char_converter import CharConverter

    converter = CharConverter("v2s")

read_file_class = FileOperation()
dy_dic = FileOperation.read_dy("DYNASTIES.txt")
office_dic = FileOperation.read_office("OFFICE_CODES.txt", dy_dic)
data_list = FileOperation.read_input("input.txt")

# add xiujunhan 2023-08-22
code_data_and_write("output.txt", data_list, office_dic)

print("done")
