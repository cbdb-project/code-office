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
                if dy not in output_dic and len(row[4])>1:
                    output_dic[dy] = [row]
                elif len(row[4])>1:
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
                if len(row[2])>1:
                    output.append(row)
        return output

    @staticmethod
    def write_data(file_name, data_list_coded):
        output = ""
        for i in data_list_coded:
            output += "\t".join(i) + "\n"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(output)

def code_data(data_list, office_dic):
    output = []
    for line in data_list:
        breaker = 0
        cbdb_office_id = "unknown"
        office_id = line[0]
        office_dy = line[1]
        office_name = line[2]
        code_status = ""
        if office_dy in office_dic:
            for cbdb_office_item in office_dic[office_dy]:
                cbdb_office_item_name_chn = cbdb_office_item[4]
                cbdb_office_item_name_id = cbdb_office_item[1]
                if office_name == cbdb_office_item_name_chn:
                    code_status = "exact"
                    cbdb_office_id = cbdb_office_item_name_id
                    output.append([office_id, office_name, office_dy, cbdb_office_id, cbdb_office_item_name_chn, code_status])
                    breaker = 1
                    break
        if office_dy in office_dic and breaker == 0:
            for cbdb_office_item in office_dic[office_dy]:
                cbdb_office_item_name_chn = cbdb_office_item[4]
                cbdb_office_item_name_id = cbdb_office_item[1]
                if cbdb_office_item_name_chn in office_name:
                    code_status = "partial"
                    cbdb_office_id = cbdb_office_item_name_id
                    output.append([office_id, office_name, office_dy, cbdb_office_id, cbdb_office_item_name_chn, code_status])
                    break
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
data_list_coded = code_data(data_list, office_dic)
FileOperation.write_data("output.txt", data_list_coded)
print("done")