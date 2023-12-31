"""
给朝代的官职加官职id

思路：
1. 根据朝代表DYNASTIES.txt，生成dy_dic[朝代id]=朝代名
2. 根据官职表OFFICE_CODES.txt、dy_dic，生成office_dic[朝代名]=官职列表
3. 官职匹配，加官职id：根据office_dic，将input.txt中的官职加上官职id、匹配类型，输出为output.txt
"""

import csv


class FileOperation:
    @staticmethod
    def read_dy(file_name):
        # 朝代名为 id
        output_dic = {}
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            for row in csv_reader:
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
                dy = dy_dic[row[2]]
                if dy not in output_dic and len(row[4]) > 1:
                    output_dic[dy] = [row]
                elif len(row[4]) > 1:
                    output_dic[dy].append(row)
                else:
                    pass
        for dy, row in output_dic.items():
            output_dic[dy] = sorted(output_dic[dy], key=lambda x: len(x[4]), reverse=True)
        return output_dic

    @staticmethod
    def read_input(file_name):
        output = []
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            for row in csv_reader:
                if len(row[2]) > 1:
                    output.append(row)
        return output

# 性能优化：生成code_data & 写入到txt
# add xiujunhan 2023-08-22
def code_data_and_write(file_name, data_list, office_dic):
    output = []
    file = open(file_name, 'w', encoding="utf-8")
    for line in data_list:
        # cbdb_office_id = "unknown"
        office_id = line[0]
        office_dy = line[1]
        office_name = line[2]
        if office_dy in office_dic:
            for cbdb_office_item in office_dic[office_dy]:
                code_status = ""
                cbdb_office_item_name_chn = cbdb_office_item[4]
                cbdb_office_item_name_id = cbdb_office_item[1]
                if office_name == cbdb_office_item_name_chn:
                    code_status = "exact"
                elif cbdb_office_item_name_chn in office_name:
                    code_status = "partial"
                if code_status != "":
                    cbdb_office_id = cbdb_office_item_name_id
                    output_row = [office_id, office_name, office_dy, cbdb_office_id, cbdb_office_item_name_chn,
                                  code_status]
                    output.append(output_row)
                    file.write("\t".join(output_row) + "\n")
                    break
    file.close()
    return output


# 未來可以嘗試實現：
# 1，帶上允許時間限制的條件；
#
# 2，如果有多項匹配，優先選擇有坐標信息的。
# （當前可以透過工程來實現這一點：把 ADDRESSES 按照 id 和 坐標（坐標由大到小）排序。坐標有值的排在前面


read_file_class = FileOperation()
dy_dic = FileOperation.read_dy("DYNASTIES.txt")
office_dic = FileOperation.read_office("OFFICE_CODES.txt", dy_dic)
data_list = FileOperation.read_input("input.txt")

# add xiujunhan 2023-08-22
code_data_and_write("output.txt", data_list, office_dic)

print("done")
