import requests

# 文件路径
file_path = "跟单系统余额.txt"
output_file_path = "跟单系统余额2.txt"  # 新的输出文件路径
api_url = "https://gmgn.ai/api/v1/wallet_holdings/sol/{}?limit=50&orderby=usd_value&direction=desc&showsmall=true&sellout=true&tx30d=true"

def fetch_usd_value(address):
    """
    根据API获取指定地址的usd_value总和，仅调用两次API
    """
    total_usd_value = 0
    next_cursor = None
    print(address)
    for _ in range(2):  # 限制调用两次
        try:
            # 如果有 next 游标，加入到请求中
            url = api_url.format(address)
            if next_cursor:
                url += f"&cursor={next_cursor}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 0 and "data" in data and "holdings" in data["data"]:
                # 累计 holdings 中的 usd_value
                holdings = data["data"]["holdings"]
                total_usd_value += sum(float(item.get("usd_value", 0)) for item in holdings)

                # 更新 next 游标，准备下次调用
                next_cursor = data["data"].get("next")
                if not next_cursor:  # 如果没有 next 游标，提前结束
                    break
            else:
                print(f"API响应错误或无数据: {response.text}")
                break
        except Exception as e:
            print(f"请求API时出错: {e}")
            break

    return total_usd_value

def update_file():
    """
    遍历文件中的地址，调用API，计算usd_value总和，并将结果保存到新文件
    """
    try:
        with open(file_path, "r") as file:
            addresses = [line.strip() for line in file.readlines()]

        updated_lines = []
        for address in addresses:
            # 处理文件中地址带有旧值的情况
            if "," in address:
                address = address.split(",")[0].strip()

            total_usd_value = fetch_usd_value(address)
            updated_lines.append(f"{address},{total_usd_value:.2f}")

        # 将更新后的内容保存到新文件
        with open(output_file_path, "w") as file:
            file.write("\n".join(updated_lines))

        print(f"文件已更新并保存到 {output_file_path}！")
    except Exception as e:
        print(f"处理文件时出错: {e}")

if __name__ == "__main__":
    update_file()
