import glob
import os


def insert_string_at_start(file_path, text_to_insert):
    try:
        with open(file_path, 'r+') as file:
            original_content = file.read()
            file.seek(0, 0)  # 将文件指针移到文件开头
            file.write(text_to_insert + '\n' + original_content)
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def clean_files():
    # 查找包含 "*rev'pmt*" 并且后缀为 ".csv" 的文件
    clean_file("*rev'pmt*.csv")
    clean_file("manual.csv")


def clean_file(pattern):
    # 获取当前工作目录
    current_directory = os.getcwd()

    del_files = glob.glob(os.path.join(current_directory, pattern))

    # 删除找到的文件
    for del_file in del_files:
        os.remove(del_file)
        print(f"已删除文件: {del_file}")


def read_invoice_list(file_path):
    invoice_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                data = parse_invoice_list_line(line)
                if data:
                    invoice_no, customer_id, amount = data
                    invoice_data[invoice_no] = [customer_id, amount]
            print(f"得到{len(invoice_data)}个invoice")
            return invoice_data
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def parse_invoice_list_line(csv_line):
    # 按逗号分隔CSV行数据
    fields = csv_line.strip().split(',')

    # 检查是否有足够的字段
    if len(fields) >= 10:
        try:
            invoice_no = fields[3].strip()
            customer_id = fields[4].strip()
            amount = float(fields[7].strip())
            return invoice_no, customer_id, amount
        except ValueError:
            return None
    else:
        return None


def read_qb_bank(file_path):
    dict_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                data = parse_qb_bank_line(line)

                if data:
                    pay_date, save_date, save_type, ref_no = data
                    dict_data[f"{pay_date},{save_date},{save_type}"] = ref_no
            print(f"得到{len(dict_data)}个银行记录")
            return dict_data
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def parse_qb_bank_line(csv_line):
    # 按逗号分隔CSV行数据
    fields = csv_line.strip().split(',')

    # 检查是否有足够的字段
    if len(fields) >= 4:
        pay_date = fields[0].strip()
        save_date = fields[1].strip()
        save_type = fields[2].strip()
        if len(fields) == 5:
            ref_no = f"{fields[3].strip()},{fields[4].strip()}".strip('\"\'')
        else:
            ref_no = fields[3].strip()
        return pay_date, save_date, save_type, ref_no
    else:
        return None


def parse_save(csv_line):
    # 按逗号分隔CSV行数据
    fields = csv_line.strip().split(',')

    # 检查是否有足够的字段
    if len(fields) >= 6:
        try:
            pay_date = fields[0].strip().replace('\ufeff', '', 1)
            save_date = fields[1].strip()
            invoice_no = fields[2].strip()
            save_type = fields[4].strip()
            amount = float(fields[6].strip())
            return pay_date, save_date, invoice_no, save_type, amount
        except ValueError:
            return None
    else:
        return None


def save_record(ref_no, invoice_no, customer_id, actual_amount, save_date, save_type, shop_amount, pay_date):
    if abs(shop_amount - actual_amount) > 0.6:
        import_line = f"{invoice_no},{customer_id},{save_date},{save_type},{actual_amount},{shop_amount},{round(abs(shop_amount - actual_amount),2)}\n"
        append_string_to_file(f"manual.csv", import_line)
    else:
        import_line = f"{ref_no},{invoice_no},{customer_id},{actual_amount},{save_date},{save_type},11104 TD Foodsup-8770\n"
        append_string_to_file(
            f"{save_type} rev'pmt {pay_date}({ref_no}).csv", import_line)


def read_save(file_path):
    data_dict = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                data = parse_save(line)
                if data:
                    pay_date, save_date, invoice_no, save_type, actual_amount = data
                    # invoice_dict[invoice_no] = [customer_id, amount]
                    # qb_bank_dict[f"{pay_date},{save_date},{save_type}"] = ref_no
                    try:
                        ref_no = qb_bank_dict[f"{pay_date},{save_date},{save_type}"]
                        customer_id, shop_amount = invoice_dict[invoice_no]
                        save_record(ref_no, invoice_no, customer_id,
                                    actual_amount, save_date, save_type, shop_amount, pay_date)
                    except KeyError:
                        append_string_to_file(
                            "manual.csv", f"{invoice_no},,,{actual_amount},,,,\n")
            return data_dict
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def open_file(file_path, mode='a'):
    try:
        file = open(file_path, mode)
        return file
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到")
        return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


def append_string_to_openedfile(file, text_to_append):
    if file:
        try:
            file.write(text_to_append)
        except Exception as e:
            print(f"发生错误: {str(e)}")


def close_file(file):
    if file:
        file.close()


def append_string_to_file(file_path, text_to_append):
    file = open_file(file_path, 'a')
    if file:
        try:
            file.write(text_to_append)
        except Exception as e:
            print(f"发生错误: {str(e)}")
        finally:
            file.close()


def insert_header_to_import_file():
    current_directory = os.getcwd()
    pattern = "*rev'pmt*.csv"
    import_files = glob.glob(os.path.join(current_directory, pattern))

    for import_file in import_files:
        insert_string_at_start(import_file,
                               "Ref No,Invoice No,Customer,Amount,Payment Date,Payment method,Deposit to Account Name")


clean_files()
# invoice_data[invoice_no] = [customer_id, amount]
invoice_dict = read_invoice_list("invoice_list.csv")
# dict_data[f"{pay_date},{save_date},{save_type}"] = ref_no
qb_bank_dict = read_qb_bank("qb_bank.csv")

read_save("save.csv")

insert_header_to_import_file()

# print(invoice_data)


# read_save("save.csv")

# qb_bank_data = read_qb_bank("qb_bank.csv")
# print(qb_bank_data)

# a = open_file("a.csv")
# for i in [1, 2, 3, 4, 5]:
#     append_string_to_file(a, f"{i}中华人民共和国\n")
# close_file(a)


# for i in [1, 2, 3, 4, 5]:
#     append_string_to_file("a.csv", f"{i}中华人民共和国\n")
#     append_string_to_file("a.csv", f"{i}中华人民共和国\n")
#     append_string_to_file("a.csv", f"{i}中华人民共和国\n")
